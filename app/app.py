import pandas as pd
import streamlit as st

from optimizer import Optimizer
from database import PersonSettings, TaskSettings, Database


def css_color_white_for_zero(float_val: float) -> str:
    color = "white" if float_val == 0 else "black"
    return f"color: {color}"


def md_heading(
        content: str, level: int, color: str = "#f63366", is_sidebar=False):

    md = f"<h{level} style='text-align: center; color: {color};'>" \
         f"{content}</h{level}>"

    if is_sidebar:
        st.sidebar.markdown(md, unsafe_allow_html=True)
    else:
        st.markdown(md, unsafe_allow_html=True)


def main():

    db = Database()

    APP_TITLE = "Auto Assignment"
    st.set_page_config(
        page_title=APP_TITLE,
        layout="wide",
        initial_sidebar_state="auto")

    md_heading(APP_TITLE, 1)

    st.info(
        ":information_source: "
        "Technical explanation of this app is provided in on Macnica's blog, "
        "which is written in Japanese language:"
        " [mathematical optimization]"
        "(https://mnb.macnica.co.jp/2021/11/Python-Staffing01.html), "
        "[application prototyping]"
        "(https://mnb.macnica.co.jp/2022/02/ai/Python-Staffing02.html)")

    st.write(
        "Developed by [***Kazuki Igeta***](https://twiitter.com/kazukiigeta)")

    st.write("")
    st.write("This app provides you automatic assignment of tasks, "
             "which is based on mathematical optimization. The following "
             "two conditions can be overwridden by uploading CSV files "
             "from the widgets on the left side bar. "
             "And the other conditions are also changable there.")

    st.write("- Person setting: names of people and their available time")
    st.write("- Task setting: names of tasks and their requiring time")

    md_heading(content="Settings", level=1, is_sidebar=True)
    st.sidebar.write("### Assignment settings")

    # Read from DB
    df_person_settings = db.read_table_to_df(PersonSettings)
    df_task_settings = db.read_table_to_df(TaskSettings)

    optimizer = Optimizer(df_person_settings=df_person_settings,
                          df_task_settings=df_task_settings)

    st.sidebar.write("")

    sr_full_name = optimizer.person_full_name()
    for full_name in sr_full_name:

        with st.sidebar.expander(full_name):
            tasks = st.multiselect(
                label="Fixed assignment",
                options=optimizer.df_task_settings["task_name"],
                key=f"fix-{full_name}")

            if len(tasks) > 0:
                sr_n_person = optimizer.sr_n_person()

                for task in tasks:
                    task_number = optimizer.task_number(task)
                    if sr_n_person[task_number] != 0:
                        max_value = (
                            float(
                                optimizer.df_task_settings
                                .query(f"task_name == '{task}'")
                                .loc[:, "hour"]
                            )
                        )
                        hour_setting = st.number_input(
                            label=f"{task} "
                                  f"man hour（0.00 means equally distribution）",
                            min_value=0.0,
                            max_value=max_value,
                            step=0.01,
                            key=f"{full_name}-{task}"
                        )

                        optimizer.fix_condition(person_full_name=full_name,
                                                task_name=task,
                                                hour=hour_setting)

        st.sidebar.write("")

    # Upload person settings CSV
    uploaded_person_settings = st.sidebar.file_uploader(
        "Upload person setting CSV", type="csv")

    if uploaded_person_settings is not None:
        df_person_for_assertion = pd.read_csv(uploaded_person_settings)

        try:
            assert (
                df_person_for_assertion.iloc[:, 0].apply(type) == str
            ).all(), (
                "the 1st column must have the last names of the people"
            )

            assert (
                df_person_for_assertion.iloc[:, 1].apply(type) == str
            ).all(), (
                "the 2nd column must have the first names of the people"
            )

            assert (
                df_person_for_assertion.iloc[:, 2].apply(type) == float
            ).all(), (
                "the 3rd column must have the numbers of "
                "the available hours of people"
            )

        except AssertionError as err:
            st.error(f"Person CSV format error: {str(err)}")
            return

        db.initialize_table_by_csv(
            PersonSettings, uploaded_person_settings)

    # Upload task settings CSV
    st.sidebar.write("")
    uploaded_task_settings = st.sidebar.file_uploader(
        "Upload task setting CSV", type="csv")

    if uploaded_task_settings is not None:
        df_task_for_assertion = pd.read_csv(uploaded_task_settings)

        try:
            assert (
                df_task_for_assertion.iloc[:, 0].apply(type) == str
            ).all(), (
                "the 1st columns must have the names of the tasks"
            )

            assert (
                df_task_for_assertion.iloc[:, 1].apply(type) == float
            ).all(), (
                "the 2nd columns must have the required hours for the tasks"
            )

        except AssertionError as err:
            st.error(f"Task CSV format error: {str(err)}")
            return

        db.initialize_table_by_csv(TaskSettings, uploaded_task_settings)

    st.sidebar.write("")
    st.sidebar.write("### Default person settings")
    st.sidebar.write(optimizer.df_person_settings
                     .style.format({"hour": "{:.2f}"}))
    st.sidebar.write("")
    st.sidebar.write("### Default task settings")
    st.sidebar.write(
        optimizer.df_task_settings.style.format({"hour": "{:.2f}"}))

    st.sidebar.write("")
    st.sidebar.write("### N. of the people adjustments")

    for p in range(optimizer.df_task_settings.shape[0]):
        task = optimizer.df_task_settings.loc[p, "task_name"]

        num = st.sidebar.slider(
            label=optimizer.df_task_settings.iloc[p, 0],
            max_value=5,
            value=int(optimizer.df_task_settings["n_people"].at[p])
        )

        optimizer.adjust_n_person(task, num)

        st.sidebar.write("")

    df_full = optimizer.exec()

    st.write("")
    md_heading(content="Diff between the result and expectation",
               level=5, color="gray")
    sr_diff = df_full.iloc[:-1, -1].values - df_person_settings["hour"]
    df_diff = pd.DataFrame(sr_diff)
    df_diff.columns = ["DIFF"]
    df_diff.index = optimizer.person_full_name()
    st.table(
        df_diff
        .T
        .style.format(formatter="{:.2f}")
    )

    st.write("")
    md_heading(content="Optimazed result", level=5, color="gray")
    st.table(
        df_full
        .T
        .style.format(formatter="{:.2f}")
        .applymap(css_color_white_for_zero),
    )

    st.write("")
    md_heading(content="Sortable view of the result", level=5, color="gray")
    st.dataframe(
        df_full
        .T
        .style.format(formatter="{:.2f}")
        .applymap(css_color_white_for_zero),
    )


if __name__ == "__main__":
    main()
