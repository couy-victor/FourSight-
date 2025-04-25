import requests
import os
import json
from dotenv import load_dotenv
import openai
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from datetime import datetime
from utils.api_utils import search_arxiv, call_groq_api

# Load environment variables
load_dotenv()

class ResearcherAgent:
    """
    Agent responsible for searching and retrieving relevant articles and information
    based on keywords and topics.
    """

    def __init__(self):
        """Initialize the ResearcherAgent with API keys and configurations."""
        # Load API keys from environment variables
        self.serper_api_key = os.getenv("SERPER_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY", "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")

        # Set OpenAI API key
        if self.openai_api_key:
            openai.api_key = self.openai_api_key

    def search_relevant_articles(self, keywords, sector, num_results=10, include_academic=True):
        """
        Search for relevant articles based on keywords and business sector.

        Args:
            keywords (list): List of keywords to search for
            sector (str): Business sector for context
            num_results (int): Number of results to return
            include_academic (bool): Whether to include academic papers from arXiv

        Returns:
            list: List of article dictionaries with title, url, source, and summary
        """
        articles = []

        # Determine how many results to get from each source
        web_results = num_results // 2 if include_academic else num_results
        academic_results = num_results - web_results if include_academic else 0

        # Get web articles
        if self.serper_api_key:
            web_articles = self._search_with_serper(keywords, sector, web_results)
            articles.extend(web_articles)
        else:
            # Return mock data for development
            mock_articles = self._mock_search_results(keywords, sector, web_results)
            articles.extend(mock_articles)

        # Get academic articles if requested
        if include_academic and academic_results > 0:
            academic_articles = self._search_academic_articles(keywords, sector, academic_results)
            articles.extend(academic_articles)

        return articles

    def _search_with_serper(self, keywords, sector, num_results):
        """
        Perform a real search using the Serper API.
        """
        search_query = " ".join(keywords) + f" {sector} industry"

        headers = {
            'X-API-KEY': self.serper_api_key,
            'Content-Type': 'application/json'
        }

        payload = {
            'q': search_query,
            'num': num_results
        }

        response = requests.post(
            'https://google.serper.dev/search',
            headers=headers,
            json=payload
        )

        if response.status_code == 200:
            search_results = response.json()
            articles = []

            # Process organic search results
            if 'organic' in search_results:
                for result in search_results['organic'][:num_results]:
                    # Get summary by scraping the page content
                    summary = self._get_page_summary(result.get('link', ''))

                    articles.append({
                        'title': result.get('title', 'No Title'),
                        'url': result.get('link', ''),
                        'source': result.get('source', 'Unknown'),
                        'summary': summary
                    })

            return articles
        else:
            print(f"Error searching with Serper: {response.status_code}")
            return self._mock_search_results(keywords, sector, num_results)

    def _get_page_summary(self, url):
        """
        Get a summary of the page content by scraping and using OpenAI.
        """
        try:
            # Fetch the page content
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                # Parse HTML
                soup = BeautifulSoup(response.text, 'html.parser')

                # Extract text from paragraphs
                paragraphs = soup.find_all('p')
                text = ' '.join([p.get_text() for p in paragraphs])

                # Truncate to avoid token limits
                text = text[:3000] + '...' if len(text) > 3000 else text

                # Use OpenAI to summarize if API key is available
                if self.openai_api_key:
                    summary = self._summarize_with_openai(text)
                    return summary
                else:
                    # Return truncated text as summary
                    return text[:300] + '...' if len(text) > 300 else text
            else:
                return "Não foi possível acessar o conteúdo da página."
        except Exception as e:
            print(f"Error getting page summary: {e}")
            return "Erro ao processar o conteúdo da página."

    def _summarize_with_openai(self, text):
        """
        Use OpenAI to summarize text.
        """
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Você é um assistente que resume artigos de forma concisa e informativa."},
                    {"role": "user", "content": f"Resuma o seguinte texto em um parágrafo curto:\n\n{text}"}
                ],
                max_tokens=150
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error summarizing with OpenAI: {e}")
            return text[:300] + '...' if len(text) > 300 else text

    def _summarize_with_groq(self, text):
        """
        Use Groq API with Llama 4 to summarize text.
        """
        try:
            prompt = f"Resuma o seguinte texto em um parágrafo curto:\n\n{text}"
            system_message = "Você é um assistente que resume artigos de forma concisa e informativa."

            summary = call_groq_api(prompt, system_message, 150)
            return summary
        except Exception as e:
            print(f"Error summarizing with Groq: {e}")
            return text[:300] + '...' if len(text) > 300 else text

    def _search_academic_articles(self, keywords, sector, num_results):
        """
        Search for academic articles using arXiv API.

        Args:
            keywords (list): List of keywords to search for
            sector (str): Business sector for context
            num_results (int): Number of results to return

        Returns:
            list: List of article dictionaries with title, url, source, and summary
        """
        # Combine keywords with sector for search
        search_query = " ".join(keywords) + f" {sector}"

        try:
            # Use arXiv API through our utility function
            papers = search_arxiv(search_query, max_results=num_results)

            # Process papers to match our article format
            articles = []

            for paper in papers:
                # Use Groq to summarize if available, otherwise use the original summary
                if len(paper['summary']) > 500:
                    summary = self._summarize_with_groq(paper['summary'])
                else:
                    summary = paper['summary']

                articles.append({
                    'title': paper['title'],
                    'url': paper['url'],
                    'source': f"arXiv ({', '.join(paper['categories'][:2])})",
                    'summary': summary,
                    'authors': paper.get('authors', []),
                    'published_date': paper.get('published_date', '')
                })

            return articles

        except Exception as e:
            print(f"Error searching academic articles: {e}")
            # Return mock academic data as fallback
            return self._mock_academic_results(keywords, sector, num_results)

    def _mock_search_results(self, keywords, sector, num_results):
        """
        Generate mock search results for development purposes.
        """
        mock_articles = [
            {
                'title': f"Inovações em {' '.join(keywords)} para o setor de {sector}",
                'url': "https://example.com/article1",
                'source': "Journal of Innovation",
                'summary': f"Este artigo explora as últimas tendências em {' '.join(keywords)} e como elas estão transformando o setor de {sector}. Empresas líderes estão adotando estas tecnologias para criar vantagens competitivas."
            },
            {
                'title': f"Como {' '.join(keywords)} está revolucionando {sector}",
                'url': "https://example.com/article2",
                'source': "Tech Insights",
                'summary': f"Uma análise profunda de como {' '.join(keywords)} está criando novas oportunidades no setor de {sector}. Casos de uso e implementações bem-sucedidas são discutidos."
            },
            {
                'title': f"O futuro de {sector} com {' '.join(keywords)}",
                'url': "https://example.com/article3",
                'source': "Future Trends",
                'summary': f"Especialistas preveem que {' '.join(keywords)} terá um impacto significativo em {sector} nos próximos 5 anos. Este artigo explora as possíveis transformações e desafios."
            }
        ]

        # Generate additional mock articles if needed
        while len(mock_articles) < num_results:
            mock_articles.append({
                'title': f"Estudo de caso: {' '.join(keywords)} em {sector}",
                'url': f"https://example.com/article{len(mock_articles) + 1}",
                'source': "Industry Reports",
                'summary': f"Um estudo de caso detalhado sobre a implementação de soluções baseadas em {' '.join(keywords)} no setor de {sector}. Resultados e lições aprendidas são compartilhados."
            })

        return mock_articles[:num_results]

    def _mock_academic_results(self, keywords, sector, num_results):
        """
        Generate mock academic results for development purposes.
        """
        mock_papers = [
            {
                'title': f"Uma Análise Sistemática de {' '.join(keywords)} no Contexto de {sector}",
                'url': "https://arxiv.org/abs/mock.2304.12345",
                'source': "arXiv (cs.AI, econ.GN)",
                'summary': f"Este artigo apresenta uma revisão sistemática da literatura sobre {' '.join(keywords)} e suas aplicações no setor de {sector}. Os autores analisam 50 estudos publicados entre 2018 e 2023, identificando padrões, desafios e oportunidades.",
                'authors': ["Maria Silva", "João Santos", "Ana Oliveira"],
                'published_date': "2023-04-15"
            },
            {
                'title': f"Inovação Disruptiva: O Papel de {' '.join(keywords)} na Transformação do Setor de {sector}",
                'url': "https://arxiv.org/abs/mock.2301.54321",
                'source': "arXiv (cs.CY, econ.EM)",
                'summary': f"Este estudo examina como {' '.join(keywords)} está causando disrupção no setor de {sector}. Através de uma análise de casos múltiplos, os autores identificam mecanismos de inovação e propõem um framework para adoção de novas tecnologias.",
                'authors': ["Carlos Mendes", "Patricia Alves"],
                'published_date': "2023-01-22"
            },
            {
                'title': f"Um Framework Conceitual para Implementação de {' '.join(keywords)} em Organizações de {sector}",
                'url': "https://arxiv.org/abs/mock.2209.98765",
                'source': "arXiv (cs.SE, econ.GN)",
                'summary': f"Este artigo propõe um framework conceitual para guiar a implementação de soluções baseadas em {' '.join(keywords)} em organizações do setor de {sector}. O framework é validado através de um estudo de caso em uma grande empresa brasileira.",
                'authors': ["Roberto Ferreira", "Camila Costa", "Lucas Martins", "Juliana Pereira"],
                'published_date': "2022-09-30"
            }
        ]

        # Generate additional mock papers if needed
        while len(mock_papers) < num_results:
            mock_papers.append({
                'title': f"Perspectivas Futuras: {' '.join(keywords)} e o Desenvolvimento do Setor de {sector}",
                'url': f"https://arxiv.org/abs/mock.2200.{len(mock_papers) + 1000}",
                'source': "arXiv (cs.CY)",
                'summary': f"Este artigo explora as tendências futuras na aplicação de {' '.join(keywords)} no setor de {sector}. Os autores discutem implicações tecnológicas, econômicas e sociais, apresentando um roadmap para os próximos 5 anos.",
                'authors': ["Nome Sobrenome", "Outro Autor"],
                'published_date': "2022-05-10"
            })

        return mock_papers[:num_results]
