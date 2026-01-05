from openai import OpenAI

from xavy.utils import load_env_vars

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
