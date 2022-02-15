import os
import pandas as pd
import psycopg2
import streamlit as st
import typing


class DBTable:
    table_name = ""
    column_names = ()


class PersonSettings(DBTable):
    table_name = "employee_settings"
    column_names = ("last_name", "first_name", "hour")


class TaskSettings(DBTable):
    table_name = "task_settings"
    column_names = ("task_name", "hour", "n_people")


class Database:
    def __init__(self):
        self.conn = psycopg2.connect(
            host="db",
            port=5432,
            dbname=os.environ["POSTGRES_DB"],
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
        )
        self.conn.autocommit = True

    def run_query(self, query: str):
        with self.conn.cursor() as cur:
            try:
                cur.execute(query)
                self.conn.commit()
                return cur.fetchall()

            except Exception:
                self.conn.rollback()

    def initialize_table_by_csv(
            self, dbtable: DBTable, csv_file: typing.TextIO):

        self.run_query(f"DELETE FROM {dbtable.table_name}")

        try:
            with self.conn.cursor() as cur:
                csv_file.seek(0)

                cur.copy_from(
                    csv_file,
                    dbtable.table_name,
                    sep=",",
                    columns=dbtable.column_names)
        except Exception as err:
            st.error(f"Error: {err}")

    def read_table_to_df(self, dbtable: DBTable) -> pd.DataFrame:
        query = f"SELECT * from {dbtable.table_name}"
        return pd.io.sql.read_sql_query(query, self.conn)
