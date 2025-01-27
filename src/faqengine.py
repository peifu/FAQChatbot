import os

import nltk
import pandas as pd
import csv
from nltk.stem.lancaster import LancasterStemmer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split as tts
from sklearn.preprocessing import LabelEncoder as LE
from sklearn.svm import SVC
from data.common import convertToLinkedText

from vectorizers.factory import get_vectoriser


class FaqEngine:
    def __init__(self, faqslist, type='tfidf'):
        self.faqslist = faqslist
        self.stemmer = LancasterStemmer()
        self.le = LE()
        self.classifier = None
        self.build_model(type)

    def cleanup(self, sentence):
        word_tok = nltk.word_tokenize(sentence)
        stemmed_words = [self.stemmer.stem(w) for w in word_tok]
        return ' '.join(stemmed_words)

    def build_model(self, type):

        self.vectorizer = get_vectoriser(type)  # TfidfVectorizer(min_df=1, stop_words='english')
        dataframeslist = [pd.read_csv(csvfile,delimiter='|',quotechar='\'').dropna() for csvfile in self.faqslist]
        #dataframeslist = [pd.read_csv(csvfile).dropna() for csvfile in self.faqslist]
        self.data = pd.concat(dataframeslist, ignore_index=True)
        self.questions = self.data['Question'].values

        questions_cleaned = []
        for question in self.questions:
            questions_cleaned.append(self.cleanup(question))

        X = self.vectorizer.vectorize(questions_cleaned)

        # Under following cases, we dont do classification
        # 'Class' column abscent
        # 'Class' column has same values
        if 'Class' not in list(self.data.columns):
            return

        y = self.data['Class'].values.tolist()
        if len(set(y)) < 2: # 0 or 1
            return

        y = self.le.fit_transform(y)

        trainx, testx, trainy, testy = tts(X, y, test_size=.0000000001, random_state=42)

        self.classifier = SVC(kernel='linear')
        self.classifier.fit(trainx, trainy)
        # print("SVC:", self.model.score(testx, testy))

    def query(self, usr):
        print("User typed : " + usr)
        exact_match_index = -1
        try:
            cleaned_usr = self.cleanup(usr)
            t_usr_array = self.vectorizer.query(cleaned_usr)
            if self.classifier:
                prediction = self.classifier.predict(t_usr_array)[0]
                class_ = self.le.inverse_transform([prediction])[0]
                # print("Class " + class_)
                questionset = self.data[self.data['Class'] == class_]
            else:
                questionset = self.data

            questionset = self.data
            # threshold = 0.7
            cos_sims = []
            i = 0
            for question in questionset['Question']:
                cleaned_question = self.cleanup(question)
                question_arr = self.vectorizer.query(cleaned_question)
                sims = cosine_similarity(question_arr, t_usr_array)
                # if sims > threshold:
                cos_sims.append(sims)
                if(cleaned_question == cleaned_usr):
                    exact_match_index = i
                i = i + 1
            # print("scores " + str(cos_sims))
            if len(cos_sims) > 0:
                ind = cos_sims.index(max(cos_sims))
                possibleQuestionList = self.getTopMatchedQuestions(cos_sims)
                if(exact_match_index >= 0 and questionset['Question'][exact_match_index] not in possibleQuestionList):
                    possibleQuestionList.insert(0,questionset['Question'][exact_match_index])

                topQuestionsHeader = "Related Questions:" + r"<br>"
                topQuestions = ""
                for question in possibleQuestionList:
                    topQuestions = topQuestions + "<li>" + convertToLinkedText(question) + r"</li>"
                if(exact_match_index < 0):
                    finalAnswer = self.data['Answer'][questionset.index[ind]]
                else:
                    finalAnswer = self.data['Answer'][exact_match_index]

                if len(possibleQuestionList) > 1:
                    finalAnswer = finalAnswer + r"<hr>" + topQuestionsHeader + "<ul>" + topQuestions + "</ul>"
                else:
                    finalAnswer = finalAnswer

                return finalAnswer
        except Exception as e:
            print(e)
            return "Could not follow your question [" + usr + "], Try again"

    def getTopMatchedQuestions(self,cos_sims):
        top_question_list = [] #set()
        tops = sorted(cos_sims, reverse=True)[:3]
        for top in tops:
            i = cos_sims.index(top)
            if i > 0:  # Found
                new_element = self.data['Question'][i]
                if new_element not in top_question_list:
                    top_question_list.append(new_element)

                print(self.data['Question'][i] + "  " + str(i) + " " + self.data['Class'][i])
            pass

        return top_question_list

def WorkinQaMode(faqs_list):
    faqmodel = FaqEngine(faqs_list, 'tfidf')
    response = faqmodel.query("Hi")
    print(response)

    while True:
       question = input("Enter Question: ")
       response = faqmodel.query(question)
       print(response)
    pass
def testOneCsvData():
    base_path = os.path.join(os.path.dirname(os.path.abspath( __file__ )),"database")
    faqs_list = [os.path.join(base_path,"ChatbotFAQ.csv")]
    WorkinQaMode(faqs_list)

def testAllCsvData():
    BASE_DIR = os.path.dirname(__file__)
    FAQs_DATA_FOLDER = os.path.join(BASE_DIR, "data")
    DATABASE_FOLDER = os.path.join(BASE_DIR, "database")
    faqs_list = [os.path.join(FAQs_DATA_FOLDER, "greetings.csv")]

    for root, directories, filenames in os.walk(DATABASE_FOLDER):
        for filename in filenames:
            file_path = os.path.join(root, filename)
            if file_path.endswith('.csv'):
                faqs_list.append(file_path)
    WorkinQaMode(faqs_list)
    pass

if __name__ == "__main__":
    testAllCsvData()
    pass


