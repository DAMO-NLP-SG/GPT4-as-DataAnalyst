import openai
import os
import shutil
import random
import re
from os import listdir
import time
import argparse
from serpapi import GoogleSearch

random.seed(42)

openai.api_key = os.environ["OPENAI_API_KEY"]



def get_gpt_result(system_role, question, max_tokens):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        max_tokens=max_tokens,
        temperature=0,
        messages=[
            {"role": "system", "content": system_role},
            {"role": "user", "content": question}
        ]
    )

    return response


def save_python(ipt):
    py_file = open("demo.py", "w")
    py_file.write(ipt)
    py_file.close()


def execute_python_code():
    os.system("python demo.py")


def find_all(a_str, sub):
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1: return
        yield start
        start += len(sub)  # use start += 1 to find overlapping matches

def extract_create_table(s):

    output = ''
    tables = s.split('CREATE TABLE')[1:]
    for table in tables:
        output += 'CREATE TABLE'
        output += table.split(');')[0]
        output += ');\n'

    return output


def query_google(query):
    key = os.environ["SERPAPI_KEY"]

    params = {
        "engine": "google",
        "q": query,
        "api_key": key,
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    if "organic_results" not in results:
        # if no organic results, return None
        return None
    else:
        # otherwise, return list of snippets
        snippets = []
        organic_results = results["organic_results"]

        for i in range(len(organic_results)):
            tmp_content = organic_results[i]

            if "snippet" in tmp_content:
                snippets.append(tmp_content["snippet"])

        return snippets



if __name__ == '__main__':
    # args
    parser = argparse.ArgumentParser()
    parser.add_argument('--id', type=int, default=0)
    # add one boolean argment
    parser.add_argument('--online', action='store_true', default=False)
    args = parser.parse_args()

    questions_1000 = open('questions_1000.txt', 'r').readlines()
    
    line = questions_1000[args.id]

    question_original = line.split('\t')[4]
    id = line.split('\t')[0]
    sql = line.split('\t')[3]

    try:
        ##### Text to SQL #####
        try:
            shutil.copyfile('/nvBench-main/database/'+sql+'/schema.sql', 'schema.sql')
        except:
            fnames = listdir('/nvBench-main/database/'+sql)
            for fname in fnames:
                if fname.endswith('.sql'):
                    shutil.copyfile('/nvBench-main/database/'+sql+'/'+fname, 'schema.sql')
        shutil.copyfile('/nvBench-main/database/'+sql+'/'+sql+'.sqlite', sql+'.sqlite')

        schema = ""
        schema_file = open('schema.sql', 'r').read()

        schema = extract_create_table(schema_file)

        database = sql+'.sqlite'

        print("*** Question ID:", id)

        system_role = '''Write python code to select relevant data and draw the chart. Please save the plot to "figure.pdf" and save the label and value shown in the graph to "data.txt".'''

        question = "Question: " + question_original + '\n\nconn = sqlite3.connect("' + database + '")\n\nSchema: \n' + schema
        print('*** Question: ', question_original, '\n')
        max_tokens = 2000

        print("*** Step1: generate code for extracting data and drawing the chart")
        input("* Press Enter to continue ...")

        start1 = time.time()
        print("* Calling GPT-4 API ...")
        response = get_gpt_result(system_role, question, max_tokens)
        text = response["choices"][0]["message"]["content"]

        # find python code
        try:
            matches = find_all(text, "```")
            matches_list = [x for x in matches]

            python = text[matches_list[0] + 10:matches_list[1]]
        except:
            python = text

        save_python(python)
        print("* Finished Step1")
        step1_time = int(time.time()-start1)
        print("* Time of Step1: ", step1_time, ' seconds\n')

        print("*** Step2: execute python code")

        input("* Press Enter to continue ...")
        start2 = time.time()
        execute_python_code()
        print("* Finished Step2")
        step2_time = int(time.time()-start2)
        print("* Time of Step2: ", step2_time, ' seconds\n')


        data = open('data.txt', 'r').read()

        print("*** Step3: generate analysis and insights")
        user_input = input("* Would you like to use online information to generate analysis and insights? (yes/no): ")

        if user_input.lower() == 'yes':
            # query online information from google
            print('* Querying online information ...')
            
            query = question_original + '\nData: \n' + data
            snippets = query_google(query)
            print("* Below is the online information:")
            for x in range(len(snippets)):
                print(str(x + 1) + ". " + snippets[x])

            question = "Question: " + question_original + '\nData: \n' + data + '\nOnline information: \n' + str(snippets)
            system_role = 'Generate analysis and insights about the data in 5 bullet points. Online information is provided but may not be relevant to the question. Only choose relevant information to generate deeper insights.'

        else:
            question = "Question: " + question_original + '\nData: \n' + data
            system_role = 'Generate analysis and insights about the data in 5 bullet points.'


        start3 = time.time()
        print('* Start generating analysis and insights ...')

        response = get_gpt_result(system_role, question, max_tokens)

        text = response["choices"][0]["message"]["content"]

        print('* Response: \n', text)
        print("* Finished Step3")
        step3_time = int(time.time()-start3)
        print("* Time of Step3: ", step3_time, ' seconds\n')

        print('*** Total time: ', step1_time + step2_time + step3_time, ' seconds\n\n')

        response_file = open('analysis.txt', 'w')
        response_file.write(text)
        response_file.close()

        shutil.move('figure.pdf','figure_' + id + '.pdf')
        shutil.move('data.txt', 'data_' + id + '.txt')
        shutil.move('analysis.txt', 'analysis_' + id + '.txt')
        shutil.move('demo.py', 'demo_' + id + '.py')

        os.remove('schema.sql')
        os.remove(sql+'.sqlite')
    except:
        try:
            shutil.move('figure.pdf','figure_' + id + '.pdf')
        except:
            None
        try:
            shutil.move('data.txt', 'data_' + id + '.txt')
        except:
            None
        try:
            shutil.move('analysis.txt', 'analysis_' + id + '.txt')
        except:
            None
        try:
            shutil.move('demo.py', 'demo_' + id + '.py')
        except:
            None
        try:
            os.remove('schema.sql')
        except:
            None
        try:
            os.remove(sql+'.sqlite')
        except:
            None
            

