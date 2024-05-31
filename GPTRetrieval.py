from openai import OpenAI
import os


class GPTRetrieval:
    def __init__(self, api_key):
        """
        Initialize the ChatGPTRetrieval class with the OpenAI API key and model.

        Parameters:
            api_key (str): OpenAI API key for authentication.
        """
        self.api_key = api_key

        self.client = OpenAI(api_key=api_key)

    def answer_from_triples(self, question, linearized_triples):
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {
                    "role": "system",
                    "content": "You will receive a question and a list of answers. You need to answer the question in natural language using the list of answers you receive. You must always include all items from the answer list in your response. If the list of answers is empty, say that the model was unable to fetch the answers."
                },
                {
                    "role": "user",
                    "content": f"Question:\n{question}\n\nList of answers: {linearized_triples}"
                }
            ],
            temperature=0,
            max_tokens=500,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        answer = response.choices[0].message.content
        return answer

    def rephrase_question(self, question):
        response = self.client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You will receive a question. The primary entity in the question will be highlighted in square brackets. You need to rephrase the question such that the user can clearly understand the flow of logic required to reach the answer of the question. The question will have links like \"directed by\", \"written by\", \"starred actors\", \"has language\", \"has genre\", \"in language\", \"has imdb rating\", \"has imdb votes\", \"release year\" which you must look for to understand the flow of logic. The rephrased question should include only a single instance of the primary entity and the primary entity must remain in square brackets."
                },
                {
                    "role": "user",
                    "content": "which person wrote the movies starred by the actors in [The Fox and the Hound 2]"
                },
                {
                    "role": "assistant",
                    "content": "which person wrote the movies whose actors also starred in [The Fox and the Hound 2]"
                },
                {
                    "role": "user",
                    "content": "which person directed the movies starred by the actors in [Stuart Little 2]"
                },
                {
                    "role": "assistant",
                    "content": "which person directed the movies whose actors also starred in [Stuart Little 2]"
                },
                {
                    "role": "user",
                    "content": "who is listed as screenwriter of the films directed by the [Dog Nail Clipper] director"
                },
                {
                    "role": "assistant",
                    "content": "who is listed as screenwriter of the films whose directer also directed [Dog Nail Clipper]"
                },
                {
                    "role": "user",
                    "content": "which person directed the movies starred by [John Krasinski]"
                },
                {
                    "role": "assistant",
                    "content": "which person directed the movies in which [John Krasinski] starred"
                },
                {
                    "role": "user",
                    "content": "who acted together with [Breckin Meyer]"
                },
                {
                    "role": "assistant",
                    "content": "who acted together with [Breckin Meyer] in a movie"
                },
                {
                    "role": "user",
                    "content": "what are the main languages in [Madame de La Fayette] written films"
                },
                {
                    "role": "assistant",
                    "content": "what are the main languages in films written by [Madame de La Fayette]"
                },
                {
                    "role": "user",
                    "content": "which screenwriters co-wrote films with [René Clément]"
                },
                {
                    "role": "assistant",
                    "content": "which screenwriters co-wrote films with [René Clément] as one of the co-writers"
                },
                {
                    "role": "user",
                    "content": "[Steven Quale] was the director of which films"
                },
                {
                    "role": "assistant",
                    "content": "which films were directed by [Steven Quale]"
                },
                {
                    "role": "user",
                    "content": "what was the release year of the movie [The Prizefighter and the Lady]"
                },
                {
                    "role": "assistant",
                    "content": "what was the release year of the movie titled [The Prizefighter and the Lady]"
                },
                {
                    "role": "user",
                    "content": question
                },
            ],
            temperature=1,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        answer = response.choices[0].message.content
        return answer

    def get_relation_seq(self, question):
        response = self.client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are query formulator. You will be given questions, the answers of while lie in a Knowledge Graph which stores data in triple format (Entity, Relation, Related-Entity). \n\nYour answer is always going to be the query that will be required to answer the given question. \n\nYou need to follow the following instructions for generating the query:\n\n1. Entities in questions are highlighted with a pair of square brackets in the text. For example, in the question - \"What movies did [Temuera Morrison] act in?\" - Temuera Morrison is the entity. \n\n2. Each knowledge graph triple is in the format: (Entity, Relation, Related-Entity).\n\n3. Unique relations in the knowledge graph include,\n\n3.1 'directed_by': Indicates the director(s) of a movie. Sample triple: (Kismet, directed_by, William Dieterle). All triples of this relation point from movie (Kismet) to director (William Dieterle).\n\n3.2 'written_by': Represents the writer(s) of a movie. Sample triple: (Kismet, written_by, Edward Knoblock). All triples of this relation point from movie (Kismet) to writer (Edward Knoblock).\n\n3.3 'starred_actors': Denotes the actors who star in a movie. Sample triple: (Kismet, starred_actors, Ronald Colman). All triples of this relation point from movie (Kismet) to actor (Ronald Colman).\n\n3.4 'release_year': Specifies the year a movie was released. Sample triple: (Kismet, release_year, 1944). All triples of this relation point from movie (Kismet) to release year (1944).\n\n3.5 'in_language': Indicates the language in which a movie is presented. Sample triple: (Kismet, in_language, English). All triples of this relation point from movie (Kismet) to language (English).\n\n3.6 'has_tags': Represents tags or keywords associated with a movie. Sample triple: (Kismet, has_tags, bd-r). All triples of this relation point from movie (Kismet) to tag (bd-r).\n\n3.7 'has_genre': Specifies the genre(s) of a movie. Sample triple: (Flags of Our Fathers, has_genre, War). All triples of this relation point from movie (Flags of Our Fathers) to genre (War).\n\n3.8 'has_imdb_votes': Denotes the number of IMDb votes a movie has received. Sample triple: (Flags of Our Fathers, has_imdb_votes, famous). All triples of this relation point from movie (Flags of Our Fathers) to imdb votes (famous).\n\n3.9 'has_imdb_rating': Represents the IMDb rating of a movie. Sample triple: (Moonlight Mile, has_imdb_rating, good). All triples of this relation point from movie (Moonlight Mile) to imdb rating (good).\n\n4. To generate the query, trace the path of relations that should be followed starting from the primary entity using the unique relation provided above.\n\n5. Your answer should always be only a list of relations in the following format: ['relation1'] for 1-hop question, ['relation1', 'relation2'] for 2-hop question, and  ['relation1', 'relation2', 'relation3']  for 3-hop question. \n\n6. For questions which require multiple iterations of the same relation, you also need to add them into the list that many times. For example, in order to answer the question \"who acted together with [Tania Raymonde]\", we will first use 'starred_actors' to go from actor to movie, and then we will use 'starred_actors' again to go from movie back to actor. Therefore, expected answer would be: ['starred_actors'. 'starred_actors']\n\n7. You must check the validity of your query by making sure that the sequence of relations indeed link with each other.\n\nFollowing are some sample questions and expected queries provided for reference:\n\nExample 1-\nQuestion: what movies did [Temuera Morrison] act in?\nQuestion Type: actor_to_movie\nExpected Answer: ['starred_actors']\n\nExample 2-\nQuestion: what are the languages spoken in the films directed by [Joel Zwick]?\nQuestion Type: director_to_movie_to_language\nExpected Answer: ['directed_by', 'in_language']\n\nExample 3-\nQuestion: the films that share directors with the film [Black Snake Moan] were in which genres?\nQuestion Type: movie_to_director_to_movie_to_genre\nExpected Answer: ['directed_by', 'directed_by', 'has_genre']\n\nExample 4-\nQuestion: which person wrote the movies whose actors also starred in [David Copperfield]\nQuestion Type: movie_to_actor_to_movie_to_director\nExpected Answer: ['starred_actors', 'starred_actors', 'written_by']\n\nExample 5-\nQuestion: who starred in the movies whose writers also wrote [The Dark Knight]\nQuestion Type: movie_to_wrter_to_movie_to_actor\nExpected Answer: ['written_by'', 'written_by'', 'starred_actors']\n\nExample 6-\nQuestion: what terms are applicable to [Quest for Camelot]\nQuestion Type: movie_to_tags\nExpected Answer: ['has_tags']\n\nExample 7-\nQuestion: what movies can be described by [bradley cooper]\nQuestion Type: tags_to_movie\nExpected Answer: ['has_tags']"
                },
                {
                    "role": "user",
                    "content": "which person wrote the movies whose actors also starred in [The Fox and the Hound 2]"
                },
                {
                    "role": "assistant",
                    "content": "['starred_actors', 'starred_actors', 'written_by']"
                },
                {
                    "role": "user",
                    "content": "which person directed the movies whose actors also starred in [Stuart Little 2]"
                },
                {
                    "role": "assistant",
                    "content": "['starred_actors', 'starred_actors', 'directed_by']"
                },
                {
                    "role": "user",
                    "content": "who is listed as screenwriter of the films whose directer also directed [Dog Nail Clipper]"
                },
                {
                    "role": "assistant",
                    "content": "['directed_by', 'directed_by', 'written_by']"
                },
                {
                    "role": "user",
                    "content": "which person directed the movies in which [John Krasinski] starred"
                },
                {
                    "role": "assistant",
                    "content": "['starred_actors', 'directed_by']"
                },
                {
                    "role": "user",
                    "content": "who acted together with [Breckin Meyer] in a movie"
                },
                {
                    "role": "assistant",
                    "content": "['starred_actors', 'starred_actors']"
                },
                {
                    "role": "user",
                    "content": "what are the main languages in films written by [Madame de La Fayette]"
                },
                {
                    "role": "assistant",
                    "content": "['written_by', 'in_language']"
                },
                {
                    "role": "user",
                    "content": "which screenwriters co-wrote films with [René Clément] as one of the co-writers"
                },
                {
                    "role": "assistant",
                    "content": "['written_by', 'written_by']"
                },
                {
                    "role": "user",
                    "content": "which films were directed by [Steven Quale]"
                },
                {
                    "role": "assistant",
                    "content": "['directed_by']"
                },
                {
                    "role": "user",
                    "content": "what was the release year of the movie titled [The Prizefighter and the Lady]"
                },
                {
                    "role": "assistant",
                    "content": "['release_year']"
                },
                {
                    "role": "user",
                    "content": "which movies can be described by [joe pantoliano]"
                },
                {
                    "role": "assistant",
                    "content": "['has_tags']"
                },
                {
                    "role": "user",
                    "content": "what words describe film [Dredd]"
                },
                {
                    "role": "assistant",
                    "content": "['has_tags']"
                },
                {
                    "role": "user",
                    "content": question
                },

            ],
            temperature=0,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        answer = response.choices[0].message.content
        return answer
