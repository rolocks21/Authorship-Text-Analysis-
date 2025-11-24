import math

class TextModel:
    """Serves as a blueprint for objects that model
       a body of text
    """
    
    def __init__(self, model_name):
        """constructs a new TextModel
        """
        self.name = model_name
        self.words = {}
        self.word_lengths = {}
        self.stems = {}
        self.sentence_lengths = {}
        self.punctuations = {}
    
    def __repr__(self):
        """returns a string representation of the TextModel
        """
        s = 'text model name: ' + self.name + '\n'
        s += '  number of words: ' + str(len(self.words)) + '\n'
        s += '  number of word lengths: ' + str(len(self.word_lengths)) + '\n'
        s += '  number of stems: ' + str(len(self.stems)) + '\n'
        s += '  number of sentence lengths: ' + str(len(self.sentence_lengths)) + '\n'
        s += '  number of punctuations: ' + str(len(self.punctuations)) + '\n'
        return s
      
    def add_string(self, s):
        """Analyzes the string txt and adds its pieces
           to all of the dictionaries in this text model
        """
        sent_word_count = 0
        sentences = 0
        words = s.split()
        
        for word in words:
            sent_word_count += 1
            if word[-1] in ('.','?','!'):
                if sent_word_count not in self.sentence_lengths:
                    self.sentence_lengths[sent_word_count] = 1
                else:
                    self.sentence_lengths[sent_word_count] += 1
            
                sent_word_count = 0
                sentences += 1
        
        if sent_word_count > 0:
            if sent_word_count not in self.sentence_lengths:
                self.sentence_lengths[sent_word_count] = 1
            else:
                self.sentence_lengths[sent_word_count] += 1
                
        word_list = clean_text(s)
        
        for w in word_list:
            if w not in self.words:
               self.words[w] = 1
            else:
                self.words[w] += 1
            
        for w in word_list:
            word_len = len(w)
            if word_len not in self.word_lengths:
                self.word_lengths[word_len] = 1
            else:
                self.word_lengths[word_len] += 1
        
        for w in word_list:
            word = stem(w)
            if word not in self.stems:
                self.stems[word] = 1
            else:
                self.stems[word] += 1
        
        new_text = punctuation_only(s)
        
        for w in new_text:
            if w not in self.punctuations:
                self.punctuations[w] = 1
            else:
                self.punctuations[w] += 1  # Fixed bug: was self.stems[word] += 1
                      
                
    def add_file(self, filename):
        """adds all of the text in the file identified
           by filename to the model
        """
        try:
            with open(filename, 'r', encoding='utf8', errors='ignore') as f:
                text = f.read()
            self.add_string(text)
        except FileNotFoundError:
            print(f"Error: File {filename} not found")
        except Exception as e:
            print(f"Error reading file {filename}: {e}")
    
    def save_model(self):
        """saves the TextModel object self by writing
           its various feature dictionaries to files
        """
        filename = self.name + '_' + 'words'
        length_filename = self.name + '_' + 'word_lengths'
        stems_filename = self.name + '_' + 'stems'
        sentence_lengths_filename = self.name + '_' + 'sentence_lengths'
        punctuations_filename = self.name + '_' + 'punctuations'
        
        f = open(filename, 'w')
        f.write(str(self.words))
        f.close()
        
        f = open(length_filename, 'w')
        f.write(str(self.word_lengths))
        f.close()
        
        f = open(stems_filename, 'w')
        f.write(str(self.stems))
        f.close()
        
        f = open(sentence_lengths_filename, 'w')
        f.write(str(self.sentence_lengths))
        f.close()
        
        f = open(punctuations_filename, 'w')
        f.write(str(self.punctuations))
        f.close()
    
    def read_model(self):
        """reads the stored dictionaries for the called
           TextModel object from their files and assigns
           them to the attributes of the called TextModel
        """
        filename = self.name + '_' + 'words'
        length_filename = self.name + '_' + 'word_lengths'
        stems_filename = self.name + '_' + 'stems'
        sentence_lengths_filename = self.name + '_' + 'sentence_lengths'
        punctuations_filename = self.name + '_' + 'punctuations'
        
        f = open(filename, 'r')
        words = f.read()
        f.close()
        
        self.words = dict(eval(words))
        
        f = open(length_filename, 'r')
        word_lengths = f.read()
        f.close()
        
        self.word_lengths = dict(eval(word_lengths))
        
        f = open(stems_filename, 'r')
        stems = f.read()
        f.close()
        
        self.stems = dict(eval(stems))
        
        f = open(sentence_lengths_filename, 'r')
        sentence_lengths = f.read()
        f.close()
        
        self.sentence_lengths = dict(eval(sentence_lengths))
        
        f = open(punctuations_filename, 'r')
        punctuations = f.read()
        f.close()
        
        self.punctuations = dict(eval(punctuations))
    
    def similarity_scores(self, other):
        """computes and returns a list of log similarity scores
           measuring the similarity of self and other
        """
        word_score = compare_dictionaries(other.words, self.words)
        word_lengths_score = compare_dictionaries(other.word_lengths, self.word_lengths)
        stem_score = compare_dictionaries(other.stems, self.stems)
        sentence_length_score = compare_dictionaries(other.sentence_lengths, self.sentence_lengths)
        punctuation_score = compare_dictionaries(other.punctuations, self.punctuations)
        
        scores = [word_score, word_lengths_score, stem_score, sentence_length_score, punctuation_score]
        
        return scores
    
    def classify(self, source1, source2):
        """compares the called TextModel object (self) to two other
           "source" TextModel objects (source1 and source2) and determines
           which of these other TextModels is the more likely source of the
           called TextModel
        """
        scores1 = self.similarity_scores(source1)
        scores2 = self.similarity_scores(source2)
        
        print('scores for', source1.name, ':', scores1)
        print('scores for', source2.name, ':', scores2)
        
        # Use weighted scores for more accurate classification
        weights = [0.3, 0.1, 0.3, 0.2, 0.1]  # words and stems are most important
        weighted_score1 = sum(s * w for s, w in zip(scores1, weights))
        weighted_score2 = sum(s * w for s, w in zip(scores2, weights))
        
        # Also keep simple vote count for comparison
        score1 = 0
        score2 = 0
        for i in range(len(scores1)):
            if scores1[i] > scores2[i]:
                score1 += 1
            elif scores1[i] < scores2[i]:
                score2 += 1
        
        print(f"Weighted scores - {source1.name}: {weighted_score1:.2f}, {source2.name}: {weighted_score2:.2f}")
        print(f"Vote count - {source1.name}: {score1}, {source2.name}: {score2}")
        
        if weighted_score1 > weighted_score2:
            print(self.name, 'is more likely to have come from', source1.name)
        else:
            print(self.name, 'is more likely to have come from', source2.name)
    
    def similarity_report(self, other):
        """provides a detailed similarity report"""
        scores = self.similarity_scores(other)
        features = ['Words', 'Word Lengths', 'Stems', 'Sentence Lengths', 'Punctuations']
        
        print(f"Similarity report: {self.name} vs {other.name}")
        print("-" * 50)
        for feature, score in zip(features, scores):
            print(f"{feature:15}: {score:8.2f}")
        print(f"{'Overall':15}: {sum(scores):8.2f}")

def sample_file_write(filename):
    """A function that demonstrates how to write a
       Python dictionary to an easily-readable file.
    """
    d = {'test': 1, 'foo': 42}   
    f = open(filename, 'w')      
    f.write(str(d))              
    f.close()    
        
def sample_file_read(filename):
    """A function that demonstrates how to read a
       Python dictionary from a file.
    """
    f = open(filename, 'r')
    d_str = f.read() 
    f.close()
    
    d = dict(eval(d_str))
    
    print("Inside the newly-read dictionary, d, we have:")
    print(d)
        
def clean_text(txt):
    """takes a string of text txt as a parameter and returns 
       a list containing the words in txt after it has been
       "cleaned"
    """
    for symbol in """.,?"'!;:()-[]{}""":
       txt = txt.replace(symbol, '')
    
    words = txt.lower().split()
    return [w for w in words if w]  # remove empty strings

def stem(s):
    """accepts a string as a parameter and returns the stem
       of s - improved version
    """
    if len(s) <= 3:
        return s
        
    # Common English suffixes in approximate order of frequency
    suffixes = [
        'iness', 'ness', 'ment', 'ing', 'ers', 'est', 
        'er', 'es', 'ed', 'ly', 's', 'y', 'e'
    ]
    
    for suffix in suffixes:
        if s.endswith(suffix) and len(s) > len(suffix) + 1:
            return s[:-len(suffix)]
    
    return s

def punctuation_only(txt):
    """takes in a string of text and leaves only the punctuation"""
    punctuation = """,.'"?!-()[]{}...:;"""
    new_text = ""
    
    for char in txt:
        if char in punctuation:
            new_text += char
        
    return new_text

def compare_dictionaries(d1, d2):
    """takes two feature dictionaries d1 and d2 as inputs, and computes
       and returns their log similarity score
    """
    if d1 == {}:
        return -50

    score = 0
    total = 0
   
    for key in d1:
        total += d1[key]
    
    for key in d2:
        if key in d1:
            in_d1 = d1[key] / total
            score += math.log(in_d1) * d2[key]
        else:
           default = 0.5 / total
           score += math.log(default) * d2[key]
           
    return score

# Example usage and testing
def test_model():
    shakespeare = TextModel("Shakespeare")
    dickens = TextModel("Dickens")

    shakespeare.add_file("shakespeare.txt")
    dickens.add_file("dickens.txt")

    mystery_text = TextModel("Mystery")
    mystery_text.add_file("unknown_work.txt")
    
test_model()