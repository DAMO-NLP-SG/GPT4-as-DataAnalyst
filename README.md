# GPT-4 as Data Analyst

This repo contains the data and code for our paper "[Is GPT-4 a Good Data Analyst?](https://arxiv.org/abs/2305.15038)".

### 1. Requirements
#### 1.1 OPENAI_API_KEY
Create an account and get the API key for OpenAI (https://openai.com).

```
OPENAI_API_KEY=YOUR_KEY
```
#### 1.2 SERPAPI_KEY
Create an account and get the API key for google retrieval (https://serpapi.com).

```
SERPAPI_KEY=YOUR_KEY
```

#### 1.3 Install requirements
```
pip install -r requirements.txt
```

#### 1.4 Download Databases
Download the sql databases from "[nvBench dataset](https://github.com/TsinghuaDatabaseGroup/nvBench)" to the current directory and name it as ```nvBench-main```.

### 2. Run the code
```
python main.py
```

### 3. Data
Our data and experimental results will be released soon.

## Citation
If the code is used in your research, please star our repo and cite our paper as follows:
```
@inproceedings{cheng2023gptda,
  title={Is GPT-4 a Good Data Analyst?},
  author={Liying Cheng and Xingxuan Li and Lidong Bing},
  booktitle={Findings of EMNLP},
  url={"https://arxiv.org/abs/2305.15038"},
  year={2023}
}
```