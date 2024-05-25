from Database import Database
from GPTRetrieval import GPTRetrieval
import ast
import re
import os
from openai import OpenAI

class GraphRAG:
    def __init__(self, db_l, api_key):
        """
        Initialize the ChatGPTRetrieval class with the OpenAI API key and model.

        Parameters:
            api_key (str): OpenAI API key for authentication.
        """
        self.db = Database(
            database=db_l[0],
            user=db_l[1],
            password=db_l[2],
            host=db_l[3],
            port=db_l[4]
        )

        self.chat_gpt = GPTRetrieval(api_key)

    def convert_gpt_response_to_list(self, gpt_response):
        try:
            relevant_relations = ast.literal_eval(gpt_response)
            return relevant_relations
        except Exception as e:
            print(e)
            print("Possible error in response relation API format")
            return None

    def convert_gpt_answer_to_list(self, gpt_answer):
        try:
            answer_list = ast.literal_eval(gpt_answer)
            return answer_list
        except Exception as e:
            print(e)
            print("Possible error in answer API format")
            return None

    def get_gpt_rephrased_question(self, question):

        rephrased_question = self.chat_gpt.rephrase_question(question)
        return rephrased_question

    def get_gpt_response(self, question):
        rephrased_question = self.get_gpt_rephrased_question(question)
        gpt_response = self.chat_gpt.get_relation_seq(rephrased_question)
        return gpt_response

    def get_gpt_answer(self, question, linearized_triples):
        gpt_answer = self.chat_gpt.answer_from_triples(
            question, linearized_triples)
        return gpt_answer

    def get_question_entity(self, question):
        pattern = r"\[([^\[\]]+)\]"
        # Use re.findall to find all matches of the pattern in the string
        matches = re.findall(pattern, question)

        if matches:
            question_entity = matches[0]
            return question_entity
        else:
            print("Error in extracting entity from question")
            return None

    def extract_1hop_triple(self, question_entity, relevant_relations):
        self.db.connect()
        # Example: Fetch users
        try:
            triples = self.db.get_1hop_triple_subject(
                question_entity, relevant_relations[0])
            if len(triples) == 0:
                triples = self.db.get_1hop_triple_object(
                    question_entity, relevant_relations[0])
            self.db.disconnect()
            return triples
        except Exception as e:
            print(e)
            self.db.disconnect()
            return None

    def linearize_triples(self, triples):
        # Join the triples with a full stop and space
        try:
            triples_with_spaces = [(s, p.replace('_', ' '), o)
                                   for s, p, o in triples]
            triple_string = '. '.join([' '.join(triple)
                                      for triple in triples_with_spaces])
            triple_string += '.'
            return triple_string
        except Exception as e:
            print(e)
            print("Error in linearizing triples")
            return None

    def traverse_from_subject(self, question_entity, relevant_relations):
        triples = []
        ending_nodes = [question_entity]
        i = 0
        while i < len(relevant_relations):
            if i % 2 == 0:
                # subject to object
                temp = []
                for node in ending_nodes:
                    n_temp = self.db.get_1hop_triple_subject(
                        node, relevant_relations[i])
                    temp = temp + n_temp

                ending_nodes = []

                for t in temp:
                    ending_nodes.append(t["object"])
                    if t not in triples:
                        triples.append(t)

            else:
                # object to subject
                temp = []
                for node in ending_nodes:
                    n_temp = self.db.get_1hop_triple_object(
                        node, relevant_relations[i])
                    temp = temp + n_temp

                ending_nodes = []

                for t in temp:
                    ending_nodes.append(t["subject"])
                    if t not in triples:
                        triples.append(t)
            i += 1

        return list(set(ending_nodes))

    def traverse_from_object(self, question_entity, relevant_relations):
        triples = []
        ending_nodes = [question_entity]
        i = 0
        while i < len(relevant_relations):
            if i % 2 == 0:
                # object to subject
                temp = []
                for node in ending_nodes:
                    n_temp = self.db.get_1hop_triple_object(
                        node, relevant_relations[i])
                    temp = temp + n_temp

                ending_nodes = []

                for t in temp:
                    ending_nodes.append(t["subject"])
                    if t not in triples:
                        triples.append(t)

            else:
                # subject to object
                temp = []
                for node in ending_nodes:
                    n_temp = self.db.get_1hop_triple_subject(
                        node, relevant_relations[i])
                    temp = temp + n_temp

                ending_nodes = []

                for t in temp:
                    ending_nodes.append(t["object"])
                    if t not in triples:
                        triples.append(t)
            i += 1

        return list(set(ending_nodes))

    def extract_answers(self, question_entity, relevant_relations):
        self.db.connect()
        # Example: Fetch users
        try:
            triples = self.db.get_1hop_triple_object(
                question_entity, relevant_relations[0])
            # start at subject

            if len(triples) == 0:
                # start at subject
                # triples = db.get_1hop_triple_object(question_entity, relevant_relations[0])
                answers = self.traverse_from_subject(
                    question_entity, relevant_relations)
            else:
                answers = self.traverse_from_object(
                    question_entity, relevant_relations)

            self.db.disconnect()

            return answers

        except Exception as e:
            print(e)
            self.db.disconnect()
            return None

    def process_question(self, question):
        gpt_response = self.get_gpt_response(question)
        # print("GPT Response : " + gpt_response)
        relevant_relations = self.convert_gpt_response_to_list(gpt_response)

        if relevant_relations:
            question_entity = self.get_question_entity(question)
            # print("Question Entity : " + question_entity)
            if question_entity:
                answers = self.extract_answers(
                    question_entity, relevant_relations)
                if answers:
                    print("The answer is ")
                    for i in answers:
                        print(i, end=", ")
                    # triples = extract_1hop_triple(question_entity, relevant_relations)
                    # print("Triples from db : " + str(triples))
                    # if triples:
                    #     linearized_triples = linearize_triples(triples)
                    #     print("Linearized triples : " + linearized_triples)

                    #     if linearized_triples:
                    #         print(linearized_triples)
                    #         answer = get_gpt_answer(question, linearized_triples)
                    #         answer_list = convert_gpt_answer_to_list(answer)
                    #         print("Final Answer : " + str(answer_list))
                else:
                    print("Error extracting answers")
            else:
                print("Error in extracting entity from question")
        else:
            print("Possible error in API response format")

    def process_question_for_testing(self, question, gpt_response, hops):
        relevant_relations = self.convert_gpt_response_to_list(gpt_response)
        if relevant_relations:
            if len(relevant_relations) == hops:
                question_entity = self.get_question_entity(question)
                # print("Question Entity : " + question_entity)
                if question_entity:
                    answers = self.extract_answers(question_entity, relevant_relations)
                    if answers:
                        return answers
                    else:
                        return "TYPE-4-Error extracting answers from db"
                else:
                    return "TYPE-3-Error in extracting entity from question"
            else:
                return "TYPE-2-Incorrect No of Hops Identified"
        else:
            return "TYPE-1-Possible error in API response format"


# def start_dialogue():
#     RAG = GraphRAG(db_l, api_key)
#     print("Hello! Ask me anything from MetaQA. Type 'exit' to end the conversation.")

#     while True:
#         question = input("\nPrompt: ")
#         if question.lower() == 'exit':
#             print("Goodbye!")
#             break
#         RAG.process_question(question)
#         # print("GraphRAG:", answer)
#         print("")


# if __name__ == '__main__':
#     start_dialogue()
