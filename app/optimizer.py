import os
import contextlib
import numpy as np
import pandas as pd
import xpress as xp
from typing import List, Tuple


class Optimizer:
    def __init__(self,
                 df_person_settings: pd.DataFrame,
                 df_task_settings: pd.DataFrame):

        self.df_person_settings = df_person_settings
        self.df_task_settings = df_task_settings

        zero_matrix = np.zeros(
            (df_person_settings.shape[0], df_task_settings.shape[0])
        )

        self.df_fix = pd.DataFrame(zero_matrix,
                                   index=self.person_full_name(),
                                   columns=df_task_settings["task_name"])

        self._sr_n_person = df_task_settings["n_people"]

    def _auto_assignments(self) -> List[Tuple[int, int]]:
        nonzero = np.nonzero(self.df_fix.values == -1)
        return list(zip(*nonzero))

    def _specific_assignments(self) -> List[Tuple[int, int]]:
        nonzero = np.nonzero(self.df_fix.values > 0)
        return list(zip(*nonzero))

    def person_number(self, full_name: str) -> int:
        return self.df_fix.index.get_loc(full_name)

    def task_number(self, task_name: str) -> int:
        return self.df_fix.columns.get_loc(task_name)

    def person_full_name(self) -> pd.Series:
        last_name = self.df_person_settings["last_name"]
        first_name = self.df_person_settings["first_name"]
        return last_name + " " + first_name

    def sr_n_person(self):
        n_specific = np.count_nonzero(self.df_fix.values > 0, axis=0)
        return self.df_task_settings["n_people"] - n_specific

    def sr_task_hour_per_person(self):
        sr_n_person = self.sr_n_person()

        return (
            self.df_task_settings["hour"]
            .subtract(self.df_fix.replace(-1, 0).sum(axis=0).values)
            .divide(sr_n_person)
            .replace([np.inf, -np.inf, np.nan], 0.0)
        )

    def sr_expected_hour(self):
        subtrahend_hour = np.zeros(self.df_fix.shape[0])

        for e in range(self.df_fix.shape[0]):
            hour = 0.0
            for p in range(self.df_fix.shape[1]):
                fixed = self.df_fix.iloc[e, p]

                if fixed >= 0:
                    hour += fixed
                else:
                    sr_task_hour = self.sr_task_hour_per_person()
                    sr_n_person = self.sr_n_person()

                    hour += float(
                        sr_task_hour[p] / sr_n_person[p])

            subtrahend_hour[e] = hour

        return (
            self.df_person_settings["hour"]
            .subtract(subtrahend_hour)
        )

    def adjust_n_person(self, task_name: str, n: int):
        task_number = self.task_number(task_name)
        self._sr_n_person.at[task_number] = n

    def fix_condition(self,
                      person_full_name: str,
                      task_name: str,
                      hour: float):

        task_number = self.task_number(task_name)

        if self.sr_n_person()[task_number] == 0:
            raise Exception("number of person exceeded the limit")

        if hour > 0.0:
            self.df_fix.loc[person_full_name, task_name] = hour
        elif hour == 0.0:
            self.df_fix.loc[person_full_name, task_name] = -1
        else:
            raise Exception("unsuported hour")

    def optimize(self,
                 sr_expected_hour: pd.Series,
                 sr_task_hour_per_person: pd.Series,
                 sr_n_person: pd.Series,
                 auto_assignments: List[Tuple[int, int]],
                 specific_asignments: List[Tuple[int, int]]):

        xp.controls.outputlog = 0

        n_people = len(sr_expected_hour)
        n_task = len(sr_task_hour_per_person)

        xs = np.array(
            [xp.var(name=f'x{i}', vartype=xp.binary)
             for i in range(n_people*n_task)]).reshape(n_people, n_task)

        targets = np.array(
            [xp.var(name=f'Target{i}')
             for i in range(n_people)]).reshape(-1, 1)

        m = xp.problem()

        m.addVariable(xs, targets)

        m.setObjective(xp.Sum(xp.abs(targets)), sense=xp.minimize)

        target_vec = xs.dot(sr_task_hour_per_person) - \
            sr_expected_hour.values

        const = [targets[i].sum() >= xp.Sum(target_vec[i])
                 for i in range(n_people)]
        const += [xp.Sum(xs.T[i]) == n for i,
                  n in enumerate(sr_n_person)]
        const += [xp.Sum(xs[i]) >= 1 for i in range(n_people)]

        const += [xs[coodinate] == 1 for coodinate in auto_assignments]
        const += [xs[coodinate] == 0 for coodinate in specific_asignments]

        m.addConstraint(const)

        with contextlib.redirect_stdout(open(os.devnull, 'w')):
            m.solve()

        df_out = pd.DataFrame(m.getSolution(xs))
        return df_out * self.sr_task_hour_per_person()

    def exec(self) -> pd.DataFrame:
        sr_expected_hour = self.sr_expected_hour()
        sr_task_hour_per_person = self.sr_task_hour_per_person()
        sr_n_person = self.sr_n_person()

        df = self.optimize(
            sr_expected_hour=sr_expected_hour,
            sr_task_hour_per_person=sr_task_hour_per_person,
            sr_n_person=sr_n_person,
            auto_assignments=self._auto_assignments(),
            specific_asignments=self._specific_assignments(),
        )

        df.index = self.person_full_name()
        df.columns = self.df_task_settings["task_name"]

        for e in range(self.df_fix.shape[0]):
            for p in range(self.df_fix.shape[1]):
                fixed = self.df_fix.iloc[e, p]

                hour = 0.0
                if fixed == 0:
                    continue
                elif fixed == -1:
                    hour = float(self.sr_task_hour_per_person().at[p])
                else:
                    hour = fixed

                df.iloc[e, p] = hour

        df.loc[:, "SUM"] = df.sum(axis=1)
        df.loc["SUM", :] = df.sum(axis=0)

        return df
