import json
import os
from datetime import datetime

class Memory:
    def __init__(self, file_path="memory.json"):
        self.file_path = file_path
        self.short_term = [] # Histórico da conversa atual
        self.long_term = self.load_memory()

    def load_memory(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_memory(self):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.long_term, f, indent=4, ensure_ascii=False)

    def add_interaction(self, user_input, ai_response):
        # Adiciona à memória de curto prazo (contexto imediato)
        self.short_term.append({"role": "user", "content": user_input})
        self.short_term.append({"role": "assistant", "content": ai_response})
        
        # Adiciona à memória de longo prazo (aprendizado permanente)
        entry = {
            "timestamp": datetime.now().isoformat(),
            "user": user_input,
            "ai": ai_response
        }
        self.long_term.append(entry)
        self.save_memory()

    def remove_last_interaction(self):
        # Remove da memória de curto prazo (últimos 2 itens: user + assistant)
        if len(self.short_term) >= 2:
            self.short_term.pop()
            self.short_term.pop()
        
        # Remove da memória de longo prazo
        if self.long_term:
            self.long_term.pop()
            self.save_memory()

    def get_context(self, limit=10):
        # Retorna as últimas 'limit' interações para o contexto
        return self.short_term[-limit*2:] # *2 porque cada interação tem user+assistant

    def search_memory(self, query):
        # Busca simples na memória (pode ser melhorada com vetores futuramente)
        results = []
        for entry in self.long_term:
            if query.lower() in entry['user'].lower() or query.lower() in entry['ai'].lower():
                results.append(f"Lembrança: Em {entry['timestamp']}, você disse '{entry['user']}' e eu respondi '{entry['ai']}'")
        return "\n".join(results[-3:]) # Retorna as 3 últimas lembranças relevantes

    def add_feedback(self, message, kind):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "feedback": kind,
            "message": message
        }
        self.long_term.append(entry)
        self.save_memory()
