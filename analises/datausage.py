#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Code using LLMs to identify academic works that used public data 
Copyright (C) 2025  Henrique S. Xavier
Contact: contato@henriquexavier.net

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""


from openai import OpenAI
from pathlib import Path
import json
import numpy as np
import pandas as pd
import datetime as dt
import re

from xavy.utils import load_env_vars


def csv2records(filename, records_cols=['titulo', 'resumo', 'palavras_chave']):
    """
    Load a file structured as CSV into a list of dicts.
    Only keep the selected columns.
    """
    
    # Load data:
    df = pd.read_csv(filename)
    # Clean abstract:
    df['resumo'] = df['resumo'].fillna('').str.replace('\r\n', ' ').str.replace('\r', ' ').str.replace('\n', ' ')
    # Export to other formats:
    records = df[records_cols].to_dict(orient='records')

    return records


def to_datetime(timestamp):
    """
    Format `timestamp` (int) into a string representing 
    date and time.
    """
    if timestamp is None:
        return None
    else:
        return dt.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    

def in2out_name(input_filename, in_suffix='gpt-in', out_suffix='gpt-out', file_extension='.jsonl'):
    """
    Create an output filename from the input filename.

    Parameters
    ----------
    input_filename : str
        Name or path of the input filename.
    in_suffix : str
        Term in `input_filename` to be replaced by `out_suffix`.
    out_suffix : str
        Term used in replacement of `in_suffix`, if existent. 
        If not, this term is added to the end of the filename 
        (before the extension).
    file_extension : str
        Input and output filename extension.

    Returns
    -------
    outfile : str
        Output filename with the substitution or appended term
        referencing output.
    """

    # If input file has the expected suffix, replace with the output file suffix:
    if input_filename.find(in_suffix) != -1:
        outfile = input_filename.replace(in_suffix, out_suffix)
    # Generic solution when no input suffix (add suffix):
    else:
        outfile = input_filename.replace(file_extension, '_' + out_suffix + file_extension)
    
    return outfile
    

def read_jsonl(path):
    """
    Read a JSONL file and return a list of dictionaries.

    Parameters
    ----------
    path : str or Path
        Path to the JSONL file.

    Returns
    -------
    list[dict]
        One dictionary per line in the file.
    """
    records = []
    with open(path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue  # skip empty lines
            try:
                #records.append(line)
                records.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON on line {line_num}") from e
    return records


def extract(usecases, key):
    """
    Given a list of dicts `usecases`, return a list of all properties 
    of the dicts stored under `key`.
    """
    values = [uc[key] for uc in usecases]
    return values


def iskeyQ(df):
    """
    Return True if columns in `df` (DataFrame or Series)
    uniquely identifies a row, and False otherwise.
    """
    Q = len(df) == len(df.drop_duplicates())
    return Q


class PublicDataUsageDetector:
    """
    An academic work inspector that uses OpenAI's LLMs to classify 
    works into "Uses public data" or "Does not use public data".
    """
    def __init__(self, model_name, key_path, prompt_template, examples_datasets, examples_data_providers, project='proj_ZwJObp10wyAmWtBSIESV70Lw', temperature=1):
        """
        Parameters
        ----------
        model_name : str
            Name of the OpenAI model to use (e.g., 'gpt-5-nano').
        key_path : str
            Path to a file containing environment variables, including
            the OpenAI API key.
        prompt_template : str
            Path to a text file containing the prompt template used
            for classification.
        examples_datasets : str
            Example dataset names used to populate the prompt template
            and guide the model's classification.
        examples_data_providers : str
            Example data provider names used to populate the prompt
            template and guide the model's classification.
        temperature : float, optional
            Sampling temperature for the language model. Higher values
            increase randomness, while lower values make the output more
            deterministic. Default is 1.
        """

        # Initial values:
        self.batch_obj = None
        self.batch_id  = None
        self.jsonl_in  = None
        self.jsonl_out = None
        
        # Save to internal attributes:
        self.model_name = model_name
        self.key_path = key_path
        self.prompt_template = prompt_template
        self.template_vars = {'examples_datasets': examples_datasets, 'examples_data_providers': examples_data_providers}
        self.temperature = temperature
        
        # Load the API key and other parameters:
        self.env = load_env_vars(key_path)
        self.env['OPENAI_PROJECT_ID'] = project

        # Create a client:
        self.client = OpenAI(api_key=self.env['OPENAI_API_KEY'], project=self.env['OPENAI_PROJECT_ID'])

        # Read template:
        with open(prompt_template, 'r') as f:
            self.template = f.read()
        

    def build_prompt(self, data_dict: dict):
        """
        Return a string containing the prompt build for classifying 
        work described in `data_dict` (dict).

        `data_dict` should contain the keys: 'titulo', 'resumo' and 'palavras_chave'.
        """
        # Create prompt:
        prompt_input = self.template_vars.copy()
        prompt_input.update(data_dict)
        prompt = self.template % prompt_input
        return prompt

    
    def inspect(self, titulo, resumo, palavras_chave):
        """
        Call OpenAI's model to classify the work with the specified 
        metadata.
        """
        
        # Create prompt:
        data_dict = {'titulo': titulo, 'resumo': resumo, 'palavras_chave': palavras_chave}
        prompt = self.build_prompt(data_dict)
        
        # Ask LLM:
        completion = self.client.chat.completions.create(model=self.model_name, temperature=self.temperature, messages=[{"role": "developer", "content": prompt}])
        # Get response:
        answer = completion.choices[0].message.content
        
        return answer

    
    def build_batch_instance(self, custom_id: str, data_dict: dict, serialize=False, endpoint='/v1/chat/completions'):
        """
        Create the payload (dict) of a batch request for a single academic work.

        Parameters
        ----------
        custom_id : str
            An ID that represents the request.
        data_dict : dict
            It should contain the keys: 'titulo', 'resumo' and 'palavras_chave'.
        serialize : bool
            If True, return a string in JSON format. Otherwise, return a dict.
        endpoint : str
            Which OpenAI's endpoint to use for the request.
        """
        prompt = self.build_prompt(data_dict)
        body = {'model': self.model_name, 'messages': [{'role': 'developer', 'content': prompt}]}
        api_request = {'custom_id': custom_id, 'method': 'POST', 'url': endpoint, 'body': body}
        if serialize == False:
            return api_request
        else:
            return json.dumps(api_request, ensure_ascii=False)

    
    def build_batch(self, data_records: list, save_to=None, id_prefix='request-', id_offset=0, endpoint='/v1/chat/completions'):
        """
        Create a string in JSONL format in which each line is a JSON 
        specifying the request for OpenAI's LLM model.

        Parameters
        ----------
        data_records : list of dict 
            Metadata of the academic works to classify. Each entry 
            should contain the keys: 'titulo', 'resumo' and 
            'palavras_chave'.
        save_to : str, Path or None
            If `save_to` (str | Path) is provided, save the JSONL to 
            the specified file and return nothing.
        id_prefix : str
            Prefix for the 'custom_id' of each request.
        id_offset : int
            The number associated to the first request in the batch.
        endpoint : str
            Which OpenAI's endpoint to use for the request.            
        """
        jsonl = '\n'.join([self.build_batch_instance(id_prefix + str(i + id_offset), d, serialize=True, endpoint=endpoint) for i, d in enumerate(data_records)])
        if save_to == None:
            return jsonl
        else: 
            with open(save_to, 'w') as f:
                f.write(jsonl)


    def upload_batch(self, data_records: list, save_to=None, id_prefix='request-', id_offset=0, endpoint='/v1/chat/completions'):
        """
        Upload a batch request for public data usage classification to 
        OpenAI's LLM model.

        Parameters
        ----------
        data_records : list of dict 
            Metadata of the academic works to classify. Each entry 
            should contain the keys: 'titulo', 'resumo' and 
            'palavras_chave'.
        save_to : str, Path or None
            If `save_to` (str | Path) is provided, save the JSONL to 
            the specified file and return nothing.
        id_prefix : str
            Prefix for the 'custom_id' of each request.
        id_offset : int
            The number associated to the first request in the batch.
        endpoint : str
            Which OpenAI's endpoint to use for the request.

        Returns
        -------
        batch_input_file : FileObject
            An OpenAI API object that describes a file uploaded to 
            OpenAI Platform. The file contain the information 
            required to run a batch.
        """            
        # Stream payload:
        if save_to == None:
            batch = self.build_batch(data_records, save_to=save_to, id_prefix=id_prefix, id_offset=id_offset, endpoint=endpoint).encode()
            batch_input_file = self.client.files.create(file=batch, purpose="batch")
        # Save a copy of payload:
        else:
            self.build_batch(data_records, save_to=save_to, id_prefix=id_prefix, id_offset=id_offset, endpoint=endpoint)
            batch_input_file = self.client.files.create(file=open(save_to, 'rb'), purpose="batch")

        return batch_input_file


    def run_batch(self, batch_file, batch_description='Public data usage detector', endpoint='/v1/chat/completions'):
        """
        Request to run the batch specified in a file previously uploaded 
        to OpenAI's platform.

        Parameters
        ----------
        batch_file : FileObject
            Object returned by the function `self.upload_batch()`.
        batch_description : str
            Description to be added to the batch's metadata.
        endpoint : str
            Which OpenAI's endpoint to use for the request.            

        Returns
        -------
        batch_obj : Batch
            An OpenAI API object that describes a batch submitted to the
            OpenAI Platform.
        """
        batch_obj = self.client.batches.create(input_file_id=batch_file.id, endpoint=endpoint, completion_window='24h', metadata={"description": batch_description})

        return batch_obj


    def inspect_batch(self, data_records: list, save_to=None, id_prefix='request-', id_offset=0, batch_description='Public data usage detector', endpoint='/v1/chat/completions'):
        """
        Schedule the classification of academic works as "Uses public data" 
        or "Does not use public data" based on the provided metadata using 
        OpenAI's batch mode.

        Parameters
        ----------
        data_records : list of dict 
            Metadata of the academic works to classify. Each entry 
            should contain the keys: 'titulo', 'resumo' and 
            'palavras_chave'.
        save_to : str, Path or None
            If `save_to` (str | Path) is provided, save the JSONL to 
            the specified file.
        id_prefix : str
            Prefix for the 'custom_id' of each request.
        id_offset : int
            The number associated to the first request in the batch.
        batch_description : str
            Description to be added to the batch's metadata.
        endpoint : str
            Which OpenAI's endpoint to use for the request.            

        Returns
        -------
        batch_obj : Batch
            An OpenAI API object that describes a batch submitted to the
            OpenAI Platform. It can be used to monitor the batch's status.
        """        
        
        batch_input_file = self.upload_batch(data_records, save_to=save_to, id_prefix=id_prefix, id_offset=id_offset, endpoint=endpoint)
        batch_obj = self.run_batch(batch_input_file, batch_description=batch_description, endpoint=endpoint)
        self.batch_obj = batch_obj
        self.batch_id  = batch_obj.id
        self.jsonl_in  = save_to

        return batch_obj


    def batch_inspect_csv(self, csv_file, save_to, id_prefix='request-', id_offset=0, batch_description='Public data usage detector', endpoint='/v1/chat/completions'):
        """
        Schedule the classification of academic works as "Uses public data" 
        or "Does not use public data" based on the provided metadata using 
        OpenAI's batch mode.

        Parameters
        ----------
        csv_file : str 
            Metadata of the academic works to classify. The CSV 
            should contain the columns: 'titulo', 'resumo' and 
            'palavras_chave'.
        save_to : str, Path or None
            If `save_to` (str | Path) is provided, save the input JSONL 
            to the specified file.
        id_prefix : str
            Prefix for the 'custom_id' of each request.
        id_offset : int
            The number associated to the first request in the batch.
        batch_description : str
            Description to be added to the batch's metadata.
        endpoint : str
            Which OpenAI's endpoint to use for the request.            

        Returns
        -------
        batch_obj : Batch
            An OpenAI API object that describes a batch submitted to the
            OpenAI Platform. It can be used to monitor the batch's status.
        """ 
        records = csv2records(csv_file)
        batch_obj = self.inspect_batch(records, save_to, id_prefix, id_offset, batch_description, endpoint)
        return batch_obj
    

    def estimate_instance_tokens(self, batch_instance):
        """
        Estimate the number of tokens in the prompt of a batch
        instance.
    
        Parameters
        ----------
        batch_instance : dict
            Dict containing all the information required for running 
            OpenAI's model on an instance work in the batch 
            configuration.
    
        Returns
        -------
        tot_tokens : int
            Number of tokens estimated from the word counts in the
            prompt.
        """
        
        text_data = ' '.join(extract(batch_instance['body']['messages'], 'content'))
        n_words = np.array([len(t.split()) for t in text_data])
        tot_words = n_words.sum()
        tot_tokens = int(tot_words / 3481 * 5069) # Based on from https://platform.openai.com/tokenizer
        
        return tot_tokens


    def estimate_batch_tokens(self, data_records: dict):
        """
        Estimate the total number of input tokens in a batch.

        Parameters
        ----------
        data_records : list of dict
            Metadata of the academic works to classify. Each entry 
            should contain the keys: 'titulo', 'resumo' and 
            'palavras_chave'.

        Returns
        -------
        batch_tokens : int
            Estimate of the total number of tokens in the prompts
            used to classify all records in the `data_records` 
            list.
        """
        tokens = [self.estimate_instance_tokens(self.build_batch_instance(str(i), d)) for i, d in enumerate(data_records)]
        #tokens = [self.build_batch_instance(str(i), d) for i, d in enumerate(data_records)]
        batch_tokens = np.sum(tokens)
        #return tokens
        return int(batch_tokens)
    
    
    def print_batch_info(self, data: dict) -> None:
        """Print batch information in a structured and readable format."""
    
        sections = {
            "GENERAL": [
                ("Batch ID", "batch_id"),
                ("Description", "description"),
                ("Model", "model"),
                ("Status", "status"),
            ],
            "TIMESTAMPS": [
                ("Created at", "created_at"),
                ("Completed at", "completed_at"),
            ],
            "FILES": [
                ("Input file", "input_file"),
                ("Output file", "output_file"),
            ],
            "INSTANCES": [
                ("Total", "instances_total"),
                ("Completed", "instances_completed"),
                ("Failed", "instances_failed"),
            ],
            "TOKENS": [
                ("Input tokens", "input_tokens"),
                ("Cached input tokens", "input_cached_tokens"),
                ("Output tokens", "output_tokens"),
                ("Reasoning tokens", "output_reasoning_tokens"),
                ("Total tokens", "total_tokens"),
            ],
        }
    
        print("=" * 60)
        print("BATCH INFORMATION")
        print("=" * 60)
    
        for section, fields in sections.items():
            print(f"\n[{section}]")
            print("-" * 60)
    
            for label, key in fields:
                value = data.get(key, "N/A")
                print(f"{label:<22}: {value}")
    
        print("\n" + "=" * 60)
        
    
    def batch_status(self, batch_id=None, verbose=True):
        """
        Retrieve batch status and return it as a dict.
        If `verbose` is true, print the results as well.
        If no `batch_id` is provided, return the status 
        of the last batch.
        """

        # Get internal batch ID if none is provided:
        if batch_id == None:
            batch_id = self.batch_id
        
        # Get status from OpenAI:
        bs = self.client.batches.retrieve(batch_id)
        
        # Parse data:
        status = dict()
        status['batch_id']    = batch_id
        status['status']      = bs.status
        status['created_at']  = to_datetime(bs.created_at)
        status['description'] = bs.metadata['description']
        status['model'] = bs.model
        status['input_file'] = bs.input_file_id
        try:
            status['completed_at'] = to_datetime(bs.completed_at)
        except Exception as e:
            print("An error occurred at 'completed_at':", e)
            print("Type of error:", type(e))
        try:
            status['output_file'] = bs.output_file_id
        except Exception as e:
            print("An error occurred at 'output_file':", e)
            print("Type of error:", type(e))
        try:
            status['instances_completed'] = bs.request_counts.completed
            status['instances_failed'] = bs.request_counts.failed
            status['instances_total']  = bs.request_counts.total
        except Exception as e:
            print("An error occurred at 'instances_*':", e)
            print("Type of error:", type(e))
        try:
            status['input_tokens'] = bs.usage.input_tokens
            status['input_cached_tokens'] = bs.usage.input_tokens_details.cached_tokens
        except Exception as e:
            print("An error occurred at 'input_tokens':", e)
            print("Type of error:", type(e))
        try:
            status['output_tokens'] = bs.usage.output_tokens
            status['output_reasoning_tokens'] = bs.usage.output_tokens_details.reasoning_tokens
        except Exception as e:
            print("An error occurred at 'output_tokens':", e)
            print("Type of error:", type(e))
        try:
            status['total_tokens'] = bs.usage.total_tokens
        except Exception as e:
            print("An error occurred at 'total_tokens':", e)
            print("Type of error:", type(e))

        self.batch_status_ = status
        
        if verbose == True:
            self.print_batch_info(status)
        
        return status


    def cancel_batch(self, batch_id=None):
        """
        Cancel a batch with the given ID. If no ID is provided,
        cancel the last batch ran with `inspect_batch()`.
        """
        # Get internal batch ID if none is provided:
        if batch_id == None:
            batch_id = self.batch_id
        
        self.client.batches.cancel(batch_id)

    
    def download_results(self, batch_id=None, save_to=None):

        # Get internal batch ID if none is provided:
        if batch_id == None:
            batch_id = self.batch_id

        # Get info about the batch:
        status = self.batch_status(batch_id, verbose=False)
        # Get output file:
        outfile = status['output_file']
        if outfile == None:
            print('No output file available.')
            return None
        
        # Retrieve results:
        file_response = self.client.files.content(outfile)
        # Set output filename:
        if save_to == None:
            save_to = in2out_name(self.jsonl_in)
        # Save results:
        try:
            file_response.write_to_file(save_to)
            print(f'Results from batch {batch_id} saved to {save_to}.')
            self.jsonl_out = save_to
        except Exception as e:
            print("An error occurred at 'write_to_file':", e)
            print("Type of error:", type(e))
        

    def run_classification(self, works_csv):
        """
        Apply the 'public data usage' detector to academic works.

        Parameters
        ----------
        works_csv : str
            Path to a CSV file of academic works (one per row) with 
            (at least) the columns 'titulo', 'resumo' and 
            'palavras_chave'.

        Returns
        -------
        batch_obj : Batch object
            Batch information from OpenAI's API.
        """
        # Derive parameters:
        gpt_in_file = in2out_name(works_csv, in_suffix='.csv', out_suffix='_gpt-in.jsonl')
        description = 'PROMPT: {:} / DATA: {:}'.format(Path(self.prompt_template).stem, Path(works_csv).stem)
        
        # Call API:
        batch_obj = self.batch_inspect_csv(works_csv, gpt_in_file, batch_description=description)

        return batch_obj
    

def binary_encode(class_series):
    """
    Map a str Series of 'Uses public data' and 'Does not use public data'
    into ones and zeros.
    """
    y = pd.Series(np.nan, index=class_series.index)
    y.loc[class_series.str.contains('Uses public data', case=False)] = 1
    y.loc[class_series.str.contains('Does not use public data', case=False)] = 0
    try:
        return y.astype(int)
    except:
        return y
    

def build_results_csv(data_file, gpt_jsonl_in, gpt_jsonl_out, save_to=None):
    """
    Join GPT classification to original data file about academic 
    works.

    Parameters
    ----------
    data_file : str
        Path to the CSV file containing the metadata about 
        the academic works that were evaluated by GPT in terms
        of public dataset usage.
    gpt_jsonl_in : str
        Path to the GPT batch input in JSONL format.
    gpt_jsonl_out : str
        Path to the GPT batch output in JSONL format, with
        classification as 'Uses public data' or 'Does nor use
        public data'.
    save_to : str or None
        If provided, save the original data with extra columns 
        'y_pred' and 'class', containing GPT's classification, 
        to a CSV file in the provided path.

    Returns
    -------
    results_df : DataFrame
        A DataFrame with the original data with extra columns 
        'y_pred' and 'class', containing GPT's classification.
    """
    
    # Load original data:
    test_df = pd.read_csv(data_file)
    # Load GPT results:
    gpt_input  = read_jsonl(gpt_jsonl_in)
    gpt_output = read_jsonl(gpt_jsonl_out)
    
    # Create a GPT classification DataFrame:
    gpt_df = pd.DataFrame()
    # Put GPT input into DataFrame:
    gpt_df['gpt_id_in']  = pd.Series(extract(gpt_input, 'custom_id'))
    gpt_df['gpt_titulo'] = pd.Series([re.findall('<TITLE>(.+)</TITLE>', g['body']['messages'][0]['content'])[0] for g in gpt_input])
    # Put GPT output into DataFrame:
    gpt_id_out = extract(gpt_output, 'custom_id')
    out_class  = pd.Series([g['response']['body']['choices'][0]['message']['content'] for g in gpt_output], index=gpt_id_out)
    out_y_pred = binary_encode(out_class)
    out_df = pd.DataFrame({'class': out_class, 'y_pred': out_y_pred}, index=gpt_id_out)
    # Join input and output:
    gpt_df = gpt_df.join(out_df, on='gpt_id_in')

    # Make sure there are only two classes:
    assert set(gpt_df['class']) == {'Uses public data', 'Does not use public data'}
    # Consistency checks:
    assert len(gpt_input) == len(gpt_output) == len(gpt_df), 'GPT input and output should be the same size and have unique custom_ids.'
    assert gpt_df.isnull().sum().sum() == 0, 'There are missing elements in GPT DataFrame after outer join.'

    # Join classification to original works:
    classified_test_df = test_df.join(gpt_df)
    # Consistency checks:
    assert len(test_df) == len(gpt_df) == len(classified_test_df), 'Original data and GPT content should be the same size and have unique indices.'
    assert classified_test_df[['class', 'y_pred']].isnull().sum().sum() == 0, 'There are academic works without GPT classification.'
    assert (classified_test_df['titulo'] == classified_test_df['gpt_titulo']).all(), 'Academic work order or titles got messed up.'

    if save_to != None:
        classified_test_df.to_csv(save_to, index=False)
    
    return classified_test_df