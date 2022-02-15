# Assigner

[Japanese README](https://github.com/kazukiigeta/Assigner#Assigner日本語README)

This app shows a concept of automatic optimized assignments for multi-tasks to balance the work time of each person.

## procedure to deploy

```shell 
git clone https://github.com/kazukiigeta/assigner
cd Assigner
pip install -r requirements.txt
docker-compose up -d
```

## system requirements

- docker
- docker-compose

## data requirements

You can change the default settings of the assignment by uploading CSV files that have the following information.

[Sample CSV](https://github.com/kazukiigeta/Assigner/tree/main/example_csv) can be your reference to prepare the data.

- employee information
  - first name
  - last name
  - available work time (hour)

- task information
  - task name
  - required work time (hour)
  - required number of people

***

# Assigner日本語README

[English README](https://github.com/kazukiigeta/Assigner#Assigner)

複数タスクに対する人員配置最適化のコンセプトを示すためのWebアプリです。

## デモ動画

![Assigner1](https://user-images.githubusercontent.com/19583681/153996482-4b9cfd71-ec71-4b92-ba0d-12e9692e296b.gif)

"Twemoji" © Twitter ([Licensed under CC BY 4.0](https://creativecommons.org/licenses/by/4.0/))

## 構築手順

```shell 
git clone https://github.com/kazukiigeta/assigner
cd Assigner
pip install -r requirements.txt
docker-compose up -d
```

## システム要件

- docker
- docker-compose

## 必要データ

以下に示す情報を持つ2つのCSVファイルによって人員配置のデフォルト設定を変更することができます。

[サンプルCSV](https://github.com/kazukiigeta/Assigner/tree/main/example_csv)を参考にしてください。

- 人員情報
  - 名
  - 姓
  - 労働可能時間（hour）

- タスク情報
  - タスク名
  - 必要時間（hour）
  - 必要人数
