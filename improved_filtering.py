"""
Funções de filtragem melhoradas para o sistema de inovação.
Este arquivo contém funções para melhorar a filtragem de relevância dos resultados.
"""

def filter_reddit_results(posts, query, max_results=5):
    """
    Filtra os resultados do Reddit para garantir que sejam relevantes para a consulta.
    
    Args:
        posts: Lista de posts do Reddit
        query: Consulta de pesquisa
        max_results: Número máximo de resultados
        
    Returns:
        Lista filtrada de resultados do Reddit
    """
    formatted_results = []
    query_parts = query.lower().split()
    
    # Verificar se a consulta está relacionada a IA na saúde
    is_health_ai_query = (("artificial intelligence" in query.lower() or "ai" in query_parts) and 
                         any(term in query.lower() for term in ["health", "healthcare", "medical"]))
    
    # Palavras-chave específicas para IA na saúde
    health_ai_keywords = [
        "artificial intelligence", "ai ", "machine learning", "ml", "deep learning", "neural network",
        "health", "healthcare", "medical", "medicine", "clinical", "hospital", 
        "patient", "diagnosis", "treatment", "doctor", "physician"
    ]
    
    for post in posts:
        if 'data' not in post:
            continue
            
        post_data = post['data']
        
        # Texto para pesquisa (título e texto do post)
        title = post_data.get('title', '').lower()
        selftext = post_data.get('selftext', '').lower()
        search_text = title + ' ' + selftext
        
        # Calcular relevância
        relevance_score = 0
        
        if is_health_ai_query:
            # Verificar termos de IA de forma mais rigorosa
            ai_terms = ["artificial intelligence", "ai ", "machine learning", "deep learning", "neural network"]
            has_ai_term = any(ai_term in search_text for ai_term in ai_terms)
            
            # Verificar termos de saúde de forma mais rigorosa
            health_terms = ["health", "healthcare", "medical", "medicine", "clinical", "hospital", "patient", "diagnosis", "treatment", "doctor", "physician"]
            has_health_term = any(health_term in search_text for health_term in health_terms)
            
            # Se não tiver ambos os temas, pular
            if not (has_ai_term and has_health_term):
                continue
            
            # Verificar se os termos estão próximos um do outro no texto
            sentences = search_text.split('.')
            has_both_in_same_sentence = False
            
            for sentence in sentences:
                has_ai_in_sentence = any(ai_term in sentence for ai_term in ai_terms)
                has_health_in_sentence = any(health_term in sentence for health_term in health_terms)
                
                if has_ai_in_sentence and has_health_in_sentence:
                    has_both_in_same_sentence = True
                    break
            
            # Dar preferência a posts que mencionam ambos os temas na mesma frase
            relevance_score = 2 if has_both_in_same_sentence else 1
            
            # Pontuação adicional por cada palavra-chave específica
            for keyword in health_ai_keywords:
                if keyword in search_text:
                    relevance_score += 1
            
            # Verificar se o título contém termos relevantes
            has_ai_in_title = any(ai_term in title for ai_term in ai_terms)
            has_health_in_title = any(health_term in title for health_term in health_terms)
            
            # Dar pontuação extra se os termos estiverem no título
            if has_ai_in_title:
                relevance_score += 2
            if has_health_in_title:
                relevance_score += 2
            if has_ai_in_title and has_health_in_title:
                relevance_score += 3  # Bônus extra por ter ambos no título
                
            # Exigir pontuação mínima de relevância mais alta
            if relevance_score < 3:
                continue
        else:
            # Para outras consultas, usar abordagem padrão
            query_keywords = query.lower().split()
            relevance_score = sum(1 for keyword in query_keywords if keyword in search_text)
            
            # Se o post não for relevante, pular
            if relevance_score == 0 and len(query_keywords) > 1:
                continue
        
        # Extrair texto do post
        snippet = post_data.get('selftext', '')
        if not snippet:
            snippet = post_data.get('title', '')
        
        # Truncar snippet se for muito longo
        if len(snippet) > 500:
            snippet = snippet[:497] + "..."
        
        # Adicionar ao resultado
        formatted_results.append({
            'title': post_data.get('title', 'Sem título'),
            'url': f"https://www.reddit.com{post_data.get('permalink', '')}",
            'original_url': f"https://www.reddit.com{post_data.get('permalink', '')}",
            'snippet': snippet,
            'created_date': post_data.get('created_utc', 0),
            'subreddit': post_data.get('subreddit', ''),
            'score': post_data.get('score', 0),
            'num_comments': post_data.get('num_comments', 0),
            'relevance_score': relevance_score,
            'source': 'Reddit',
            'type': 'social'
        })
    
    # Ordenar por relevância (mais relevantes primeiro)
    formatted_results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
    
    # Limitar ao número máximo de resultados
    return formatted_results[:max_results]
