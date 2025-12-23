import os
from openai import OpenAI
from config import API_KEY, API_BASE_URL, MODEL_NAME, USER_NAME
from core.persona import get_system_prompt
from core.tools import Tools

class Brain:
    def __init__(self, memory):
        self.client = OpenAI(
            base_url=API_BASE_URL,
            api_key=API_KEY if API_KEY != "sk-..." else "sk-dummy" # Evita erro se chave não configurada
        )
        self.memory = memory
        self.tools = Tools()
        self.system_prompt = get_system_prompt()

    def think(self, user_input):
        # 1. Recuperar contexto
        context_messages = self.memory.get_context()
        
        # 2. Construir mensagens para a API
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # Adicionar contexto de memória
        messages.extend(context_messages)
        
        # Adicionar input atual COM IDENTIFICAÇÃO DO USUÁRIO
        messages.append({"role": "user", "content": f"[{USER_NAME} (Seu Criador/Deus)]: {user_input}"})

        print("[SISTEMA] Pensando...")
        
        try:
            # Primeira chamada para decidir o que fazer
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                temperature=0.7
            )
            
            ai_content = response.choices[0].message.content
            
            if "[SEARCH:" in ai_content:
                start = ai_content.find("[SEARCH:") + len("[SEARCH:")
                end = ai_content.find("]", start)
                query = ai_content[start:end].strip()
                
                search_result = self.tools.search_web(query)
                
                messages.append({"role": "assistant", "content": ai_content})
                messages.append({"role": "system", "content": f"RESULTADO DA PESQUISA: {search_result}\nAgora responda ao usuário com base nisso."})
                
                print("[SISTEMA] Analisando resultados da pesquisa...")
                response_final = self.client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=messages,
                    temperature=0.7
                )
                ai_content = response_final.choices[0].message.content

            return ai_content

        except Exception as e:
            return f"Erro cognitivo: {str(e)}. Verifique a API Key e a URL no config.py."

    def think_stream(self, user_input):
        """
        Versão streaming do método think.
        Retorna um gerador que produz pedaços (chunks) da resposta em tempo real.
        """
        # 1. Recuperar contexto
        context_messages = self.memory.get_context()
        
        # 2. Construir mensagens
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        messages.extend(context_messages)
        messages.append({"role": "user", "content": f"[{USER_NAME} (Seu Criador/Deus)]: {user_input}"})

        print("[SISTEMA] Pensando (Stream)...")
        
        try:
            stream = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                temperature=0.7,
                stream=True
            )
            
            full_response = ""
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield content
            
            # Verificação de Tool Use após o primeiro stream
            if "[SEARCH:" in full_response:
                start = full_response.find("[SEARCH:") + len("[SEARCH:")
                end = full_response.find("]", start)
                query = full_response[start:end].strip()
                
                # Feedback visual no stream
                yield f"\n\n_🔎 Pesquisando: {query}..._\n\n"
                
                search_result = self.tools.search_web(query)
                
                messages.append({"role": "assistant", "content": full_response})
                messages.append({"role": "system", "content": f"RESULTADO DA PESQUISA: {search_result}\nAgora responda ao usuário com base nisso."})
                
                print("[SISTEMA] Analisando resultados da pesquisa (Stream)...")
                stream2 = self.client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=messages,
                    temperature=0.7,
                    stream=True
                )
                
                for chunk in stream2:
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        yield content
                        
        except Exception as e:
            yield f"\n[ERRO] Erro cognitivo: {str(e)}"
