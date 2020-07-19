# Author: Maximillian Marciel
# Description: A basic lexer for the language "MyPL" which
#              evaluates input in MyPL and tokenizes it,
#              returning tokens as necessary and errors if needed.

import mypl_token as token
import mypl_error as error

class Lexer(object):

    def __init__(self, input_stream):
        self.line = 1
        self.column = 0
        self.input_stream = input_stream
		
    def __peek(self):
        pos = self.input_stream.tell()
        symbol = self.input_stream.read(1)
        self.input_stream.seek(pos)
        return symbol
		
    def __read(self):
        return self.input_stream.read(1)
		
    def next_token(self):
        symbol = self.__read()
        symbolAfter = self.__peek()
        self.column = self.column + 1
		
        if symbol == '\n':
            self.line = self.line + 1
            self.column = 1
            return self.next_token()
		
		#-----------------STRING-READING------------
        if symbol == '"':
            stringWord = str('')
            nextSymbol = self.__peek()
			
            while not nextSymbol == '"':
                symbol = self.__read()
                self.column = self.column + 1
                stringWord = stringWord + symbol
                nextSymbol = self.__peek()
                if symbol == '\n':
                    raise error.MyPLError("Reached newline reading string", self.line, self.column)
                if symbol == '':
                    raise error.MyPLError("Reached EOS reading string", self.line, self.column)
					
            self.__read()
            self.column = self.column + 1
            wordLength = len(stringWord) + 1
            return token.Token(token.STRINGVAL, stringWord, str(self.line), str(self.column - wordLength - 1))
			
		#-----------------DOUBLE-SYMBOLS------------
		
        elif symbol == '=' and symbolAfter == '=':
            self.__read()
            self.column = self.column + 1
            return token.Token(token.EQUAL, "==", str(self.line), str(self.column - 2))
        elif symbol == '>' and symbolAfter == '=':
            self.__read()
            self.column = self.column + 1
            return token.Token(token.GREATER_THAN_EQUAL, ">=", str(self.line), str(self.column - 2))
        elif symbol == '<' and symbolAfter == '=':
            self.__read()
            self.column = self.column + 1
            return token.Token(token.LESS_THAN_EQUAL, "<=", str(self.line), str(self.column - 2))
        elif symbol == '!' and symbolAfter == '=':
            self.__read()
            self.column = self.column + 1
            return token.Token(token.NOT_EQUAL, "!=", str(self.line), str(self.column - 2))
		
		#-----------------SINGLE-SYMBOLS------------
        elif symbol == '(':
            return token.Token(token.LPAREN, symbol, str(self.line), str(self.column - 1))
        elif symbol == '=':
            return token.Token(token.ASSIGN, symbol, str(self.line), str(self.column - 1))
        elif symbol == ')':
            return token.Token(token.RPAREN, symbol, str(self.line), str(self.column - 1))
        elif symbol == ';':
            return token.Token(token.SEMICOLON, symbol, str(self.line), str(self.column - 1))
        elif symbol == ',':
            return token.Token(token.COMMA, symbol, str(self.line), str(self.column - 1))
        elif symbol == ':':
            return token.Token(token.COLON, symbol, str(self.line), str(self.column - 1))
        elif symbol == '/':
            return token.Token(token.DIVIDE, symbol, str(self.line), str(self.column - 1))
        elif symbol == '.':
            return token.Token(token.DOT, symbol, str(self.line), str(self.column - 1))
        elif symbol == '>':
            return token.Token(token.GREATER_THAN, symbol, str(self.line), str(self.column - 1))
        elif symbol == '<':
            return token.Token(token.LESS_THAN, symbol, str(self.line), str(self.column - 1))
        elif symbol == '-':
            return token.Token(token.MINUS, symbol, str(self.line), str(self.column - 1))
        elif symbol == '%':
            return token.Token(token.MODULO, symbol, str(self.line), str(self.column - 1))
        elif symbol == '*':
            return token.Token(token.MULTIPLY, symbol, str(self.line), str(self.column - 1))
        elif symbol == '+':
            return token.Token(token.PLUS, symbol, str(self.line), str(self.column - 1))
        elif symbol == '<':
            return token.Token(token.LESS_THAN, symbol, str(self.line), str(self.column - 1))
		
		#-----------------IGNORABLES--------------------
        elif symbol.isspace():
            return self.next_token()
        elif symbol == '#':
            nextSymbol = self.__peek()
            while nextSymbol != '\n':
                nextSymbol = self.__peek()
                self.__read()
            self.line = self.line + 1
            return self.next_token()
        
		#-----------------KEYWORDS-------------------
        elif symbol.isalpha():
            word = symbol
            nextSymbol = self.__peek()

            while nextSymbol.isalpha() or nextSymbol == '_' or nextSymbol.isdigit():
                symbol = self.__read()
                self.column = self.column + 1
                word = word + symbol
                nextSymbol = self.__peek()
                if symbol == '':
                    break
					
			#evaluates the word
            wordLength = int(len(word))

            if word == "true":
                return token.Token(token.BOOLVAL, word, str(self.line), str(self.column - wordLength))
            elif word == "false":
                return token.Token(token.BOOLVAL, word, str(self.line), str(self.column - wordLength))
            elif word == "and":
                return token.Token(token.AND, word, str(self.line), str(self.column - wordLength))
            elif word == "or":
                return token.Token(token.OR, word, str(self.line), str(self.column - wordLength))
            elif word == "not":
                return token.Token(token.NOT, word, str(self.line), str(self.column - wordLength))
            elif word == "while":
                return token.Token(token.WHILE, word, str(self.line), str(self.column - wordLength))
            elif word == "do":
                return token.Token(token.DO, word, str(self.line), str(self.column - wordLength))
            elif word == "if":
                return token.Token(token.IF, word, str(self.line), str(self.column - wordLength))
            elif word == "then":
                return token.Token(token.THEN, word, str(self.line), str(self.column - wordLength))
            elif word == "else":
                return token.Token(token.ELSE, word, str(self.line), str(self.column - wordLength))
            elif word == "elif":
                return token.Token(token.ELIF, word, str(self.line), str(self.column - wordLength))
            elif word == "end":
                return token.Token(token.END, word, str(self.line), str(self.column - wordLength))
            elif word == "fun":
                return token.Token(token.FUN, word, str(self.line), str(self.column - wordLength))
            elif word == "var":
                return token.Token(token.VAR, word, str(self.line), str(self.column - wordLength))
            elif word == "set":
                return token.Token(token.SET, word, str(self.line), str(self.column - wordLength))
            elif word == "return":
                return token.Token(token.RETURN, word, str(self.line), str(self.column - wordLength))
            elif word == "new":
                return token.Token(token.NEW, word, str(self.line), str(self.column - wordLength))
            elif word == "nil":
                return token.Token(token.NIL, word, str(self.line), str(self.column - wordLength))
            elif word == "float":
                return token.Token(token.FLOATTYPE, word, str(self.line), str(self.column - wordLength))
            elif word == "int":
                return token.Token(token.INTTYPE, word, str(self.line), str(self.column - wordLength))
            elif word == "string":
                return token.Token(token.STRINGTYPE, word, str(self.line), str(self.column - wordLength))
            elif word == "struct":
                return token.Token(token.STRUCTTYPE, word, str(self.line), str(self.column - wordLength))
            elif word == "bool":
                return token.Token(token.BOOLTYPE, word, str(self.line), str(self.column - wordLength))
            else:
                return token.Token(token.ID, word, str(self.line), str(self.column - wordLength))

		#-----------------INTVAL-FLOATVAL------------
        elif symbol.isdigit():
            number = symbol
            nextSymbol = self.__peek()
            isFloat = False
            valid_symbols = "*/-+%(). ;=<>,"
			
            if not nextSymbol.isdigit() and not nextSymbol.isspace():
                if not nextSymbol in valid_symbols:
                    raise error.MyPLError("unexpected symbol %s" % (nextSymbol), self.line, self.column - 1)
			
            if symbol == '0' and nextSymbol.isdigit():
                raise error.MyPLError("unexpected symbol %s" % (nextSymbol), self.line, self.column - 1)
			
            while nextSymbol.isdigit() or nextSymbol == '.':
                symbol = self.__read()
                self.column = self.column + 1
                number = number + symbol
                nextSymbol = self.__peek()
                if symbol == '.':
                    isFloat = True
                    if not nextSymbol.isdigit():
                        raise error.MyPLError("missing digit in float value", self.line, self.column)	
                if symbol == '':
                    break
                if not nextSymbol.isdigit() and not nextSymbol.isspace():
                    if not nextSymbol in valid_symbols:
                        raise error.MyPLError("unexpected symbol %s" % (nextSymbol), self.line, self.column)

            if isFloat == True:
                numLength = int(len(number))
                return token.Token(token.FLOATVAL, number, str(self.line), str(self.column - numLength))
            else:
                numLength = int(len(number))
                return token.Token(token.INTVAL, number, str(self.line), str(self.column - numLength))
			
		#------------------EOS----------------------
        elif symbol == '':
            return token.Token(token.EOS, "", str(self.line), str(self.column - 1))
			
		#------------------UNEXPECTED----------------------
        else:
            raise error.MyPLError("unexpected symbol %s" % (symbol), self.line, self.column - 1)
		
        
            
        
			
			
			
			
			
			
			
			
			
			
			
