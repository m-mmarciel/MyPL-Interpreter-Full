# Maximillian Marciel
# Recursive Descent Parser for
# the MyPL language which checks for
# syntax and returns appropriate errors
# 2/14/19

import mypl_error as error
import mypl_lexer as lexer
import mypl_token as token
import mypl_ast   as ast

class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = None
			
    def parse(self):
        """succeeds if program is syntactically well-formed"""
        StmtList_node = ast.StmtList()
        self.__advance()
        self.__stmts(StmtList_node)
        self.__eat(token.EOS, 'expecting end of file')
        return StmtList_node
		
    def __advance(self):
        self.current_token = self.lexer.next_token()
			
    def __eat(self, tokentype, error_msg):
        if self.current_token.tokentype == tokentype:
            self.__advance()
        else:
            self.__error(error_msg)
				
    def __error(self, error_msg):
        s = error_msg + ', found "' + self.current_token.lexeme + '" in parser'
        l = self.current_token.line
        c = self.current_token.column
        raise error.MyPLError(s, int(l), int(c))
		
	#-----------------------------------------------------------------------		
    # Beginning of recursive descent functions
	#-----------------------------------------------------------------------
		
    def __stmts(self, StmtList_node): #returns the statement list
        """<stmts> ::= <stmt> <stmts> | e"""
        if self.current_token.tokentype != token.EOS:
            StmtList_node.stmts.append(self.__stmt())
            self.__stmts(StmtList_node)
						
    def __stmt(self): #Returns a statement
        """<stmt> ::= <sdecl> | <fdecl> | <bstmt>"""
        if self.current_token.tokentype == token.STRUCTTYPE:
            StructDeclStmt_node = ast.StructDeclStmt()
            StructDeclStmt_node = self.__sdecl(StructDeclStmt_node)
            return StructDeclStmt_node
            
        elif self.current_token.tokentype == token.FUN:
            FunDeclStmt_node = ast.FunDeclStmt()
            FunDeclStmt_node = self.__fdecl(FunDeclStmt_node)
            return FunDeclStmt_node
        else:
            aStmt = self.__bstmt()
            return aStmt
				
    def __sdecl(self, StructDeclStmt_node): #returns a StructDeclStmt
        """<sdecl> ::= STRUCT ID <vdecls> END""" #returns a struct decl statement
        self.__eat(token.STRUCTTYPE, "expected struct declaration")
        StructDeclStmt_node.struct_id = self.current_token
        self.__eat(token.ID, "expected identifier")
        StructDeclStmt_node.var_decls = self.__vdecls([]) #vdecls returns a list, receives an empty list
        self.__eat(token.END, "expected end statement")
        return StructDeclStmt_node
		
    def __vdecls(self, vdecl_list): #returns a list of vdecls
        """<vdecls> ::= <vdecl> <vdecls> | E""" #returns a list of vdecls 
        if self.current_token.tokentype == token.VAR:
            VarDeclStmt_node = ast.VarDeclStmt()
            VarDeclStmt_node = self.__vdecl(VarDeclStmt_node)
            vdecl_list.append(VarDeclStmt_node)
            vdecl_list = self.__vdecls(vdecl_list)
        return vdecl_list
	
    def __bstmts(self, StmtList_node): #returns a list of statements 
        """<bstmts> ::= <bstmt> <bstmts> | E"""
        bstList = [token.VAR, token.SET, token.IF, token.WHILE, token.LPAREN, token.PLUS,
        token.MINUS, token.DIVIDE, token.MULTIPLY, token.MODULO, token.STRINGVAL, token.INTVAL,
        token.BOOLVAL, token.FLOATVAL, token.NIL, token.NEW, token.ID, token.RETURN]
		
        #if self.current_token.tokentype != token.EOS:
        if self.current_token.tokentype in bstList:
            StmtList_node.stmts.append(self.__bstmt())
            self.__bstmts(StmtList_node)
        return StmtList_node

    def __bstmt(self): #returns a statement of some variation
        """<bstmt> ::= <vdecl> | <assign> | <cond> | <while> | <expr> SEMICOLON | <exit>"""
        expressionList = [token.LPAREN, token.PLUS, token.MINUS, token.DIVIDE, token.MULTIPLY,
        token.MODULO, token.STRINGVAL, token.INTVAL, token.BOOLVAL, token.FLOATVAL, token.NIL,
        token.NEW, token.ID]
        
        if self.current_token.tokentype == token.VAR:
            VarDeclStmt_node = ast.VarDeclStmt()
            VarDeclStmt_node = self.__vdecl(VarDeclStmt_node)
            return VarDeclStmt_node
        elif self.current_token.tokentype == token.SET:
            AssignStmt_node = ast.AssignStmt()
            AssignStmt_node = self.__assign()
            return AssignStmt_node
        elif self.current_token.tokentype == token.IF:
            IfStmt_node = ast.IfStmt()
            IfStmt_node = self.__cond()
            return IfStmt_node
        elif self.current_token.tokentype == token.WHILE:
            WhileStmt_node = ast.WhileStmt()
            WhileStmt_node = self.__while()
            return WhileStmt_node
        elif (self.current_token.tokentype in expressionList):
            ExprStmt_node = ast.ExprStmt()
            ExprStmt_node.expr = self.__expr()
            self.__eat(token.SEMICOLON, "expected semicolon")
            return ExprStmt_node
        else:
            ReturnStmt_node = ast.ReturnStmt()
            ReturnStmt_node = self.__exit()
            return ReturnStmt_node			
		
    def __fdecl(self, FunDeclStmt_node): #returns the FunDeclStmt
        """<fdecl> ::= FUN ( <type> | NIL) ID LPAREN <params> RPAREN <bstmts> END"""
        typeList = [token.ID, token.INTTYPE, token.FLOATTYPE, token.BOOLTYPE, token.STRINGTYPE]
		
        self.__eat(token.FUN, "expected function declaration")
        if self.current_token.tokentype in typeList:
            FunDeclStmt_node.return_type = self.__type()
        else:
            FunDeclStmt_node.return_type = self.current_token
            self.__eat(token.NIL, "expected nil")
        
        FunDeclStmt_node.fun_name = self.current_token
        self.__eat(token.ID, "expected a function identifier")
        self.__eat(token.LPAREN, "expected left parenthesis")
        FunDeclStmt_node.params = self.__params(FunDeclStmt_node.params)
        self.__eat(token.RPAREN, "expected right parenthesis")
        FunDeclStmt_node.stmt_list = self.__bstmts(FunDeclStmt_node.stmt_list)
        self.__eat(token.END, "expected end statement")
        return FunDeclStmt_node
        
		
    def __params(self, theList): #returns a list of FunParams
        """<params> ::= ID COLON <type> ( COMMA ID COLON <type> )* | E"""
        FunParam_node = ast.FunParam()
		
        if self.current_token.tokentype == token.ID:
            FunParam_node.param_name = self.current_token
            self.__eat(token.ID, "expected parameter identifier")
            self.__eat(token.COLON, "expected a colon")
            FunParam_node.param_type = self.__type()
            theList.append(FunParam_node)
            while self.current_token.tokentype == token.COMMA:
                FunParam_node = ast.FunParam()
                self.__eat(token.COMMA, "expected comma between parameters")
                FunParam_node.param_name = self.current_token
                self.__eat(token.ID, "expected identifier")
                self.__eat(token.COLON, "expected a colon")
                FunParam_node.param_type = self.__type()
                theList.append(FunParam_node)
        return theList
				
    def __type(self): #returns the type (token)
        """<type> ::= ID | INTTYPE | FLOATTYPE | BOOLTYPE | STRINGTYPE"""
        theType = self.current_token
        if self.current_token.tokentype == token.ID:
            self.__eat(token.ID, "expected an identifier")
            return theType
        elif self.current_token.tokentype == token.INTTYPE:
            self.__eat(token.INTTYPE, "expected an integer type")
            return theType
        elif self.current_token.tokentype == token.FLOATTYPE:
            self.__eat(token.FLOATTYPE, "expected a float type")
            return theType
        elif self.current_token.tokentype == token.BOOLTYPE:
            self.__eat(token.BOOLTYPE, "expected a bool type")
            return theType
        else:
            self.__eat(token.STRINGTYPE, "expected a string type")
            return theType
			
    def __exit(self): #returns a return stmt
        """<exit> ::= RETURN ( <expr> | E ) SEMICOLON"""
        expressionList = [token.LPAREN, token.PLUS, token.MINUS, token.DIVIDE, token.MULTIPLY,
        token.MODULO, token.STRINGVAL, token.INTVAL, token.BOOLVAL, token.FLOATVAL, token.NIL,
        token.NEW, token.ID]
        ReturnStmt_node = ast.ReturnStmt()

        self.__eat(token.RETURN, "expected return statement")
        if self.current_token.tokentype in expressionList:
            ReturnStmt_node.return_token = self.current_token #?????????? not sure where to put this
            ReturnStmt_node.return_expr = self.__expr()
        self.__eat(token.SEMICOLON, "expected semicolon")
        return ReturnStmt_node

    def __vdecl(self, VarDeclStmt_node):  #returns a VarDeclStmt
        """<vdecl> ::= VAR ID <tdecl> ASSIGN <expr> SEMICOLON"""
        self.__eat(token.VAR, "expected var statement")
        VarDeclStmt_node.var_id = self.current_token
        self.__eat(token.ID, "expected variable identifier")
        VarDeclStmt_node.var_type = self.__tdecl() #must return a type [done]
        self.__eat(token.ASSIGN, "expected a '='")
        VarDeclStmt_node.var_expr = self.__expr() #returns an expr (different from ExprStmt) [done]
        self.__eat(token.SEMICOLON, "expected semicolon")
        return VarDeclStmt_node
		
    def __tdecl(self): #returns a type
        """<tdecl> ::= COLON <type> | E"""
        if self.current_token.tokentype == token.COLON:
            self.__eat(token.COLON, "expected a colon")
            return self.__type()
		
    def __assign(self): #returns an AssignStmt
        """<assign> ::= SET <lvalue> ASSIGN <expr> SEMICOLON"""
        AssignStmt_node = ast.AssignStmt()
		
        self.__eat(token.SET, "expected 'set'")
        AssignStmt_node.lhs = self.__lvalue()
        self.__eat(token.ASSIGN, "expected an assignment")
        AssignStmt_node.rhs = self.__expr()
        self.__eat(token.SEMICOLON, "expected a semicolon")
        return AssignStmt_node

    def __lvalue(self): #returns an LValue node
        """<lvalue> ::= ID (DOT ID)*"""
        LValue_node = ast.LValue()
        LValue_node.path.append(self.current_token)
        self.__eat(token.ID, "expected identifier")
        while self.current_token.tokentype == token.DOT:
            self.__eat(token.DOT, "expected a dot")
            LValue_node.path.append(self.current_token)
            self.__eat(token.ID, "expected an identifier")
        return LValue_node
			
    def __cond(self): #returns an IfStmt, constructs it from basicif.
        """<cond> ::= IF <bexpr> THEN <bstmts> <condt> END"""
        IfStmt_node = ast.IfStmt()
        BasicIf_node = ast.BasicIf()

        self.__eat(token.IF, "expected if statement")
        BasicIf_node.bool_expr = self.__bexpr()
        self.__eat(token.THEN, "expected then statement")
        BasicIf_node.stmt_list = self.__bstmts(BasicIf_node.stmt_list) #bstmts returns a list of statements (StmtList)
        IfStmt_node.if_part = BasicIf_node
        IfStmt_node = self.__condt(IfStmt_node) #returns an IfStmt
        self.__eat(token.END, "expected end statement")
        return IfStmt_node
		
    def __condt(self, IfStmt_node): #returns an IfStmt, receives an IfStmt
        """ <condt> ::= ELIF <bexpr> THEN <bstmts> <condt> | ELSE <bstmts> | E"""
        BasicIf_node = ast.BasicIf()
		
        if self.current_token.tokentype == token.ELIF: #Constructs a basicIf and appends
            IfStmt_node.has_elseifs = True 
            self.__eat(token.ELIF, "expected elif")
            BasicIf_node.bool_expr = self.__bexpr()
            self.__eat(token.THEN, "expected then")
            BasicIf_node.stmt_list = self.__bstmts( BasicIf_node.stmt_list)
            IfStmt_node.elseifs.append(BasicIf_node)
            IfStmt_node = self.__condt(IfStmt_node)
        elif self.current_token.tokentype == token.ELSE:
            IfStmt_node.has_else = True
            self.__eat(token.ELSE, "expected else")
            IfStmt_node.else_stmts = self.__bstmts(IfStmt_node.else_stmts)
        return IfStmt_node
		
    def __while(self):
        WhileStmt_node = ast.WhileStmt()
        self.__eat(token.WHILE, "expected while")
        WhileStmt_node.bool_expr = self.__bexpr()
        self.__eat(token.DO, "expected do")
        WhileStmt_node.stmt_list = self.__bstmts(WhileStmt_node.stmt_list)
        self.__eat(token.END, "expected an end statement")
        return WhileStmt_node

    def __expr(self): #is an expr (abstract) different from ExprStmt
        """<expr> ::= ( <rvalue> | LPAREN <expr> RPAREN) ( <mathrel> <expr> | e)"""
		
        rvalueList = [token.STRINGVAL, token.INTVAL, token.BOOLVAL, token.FLOATVAL,
        token.NIL, token.NEW, token.ID]
        mathrelList = [token.PLUS, token.MINUS, token.DIVIDE, token.MULTIPLY, token.MODULO]
        Expr_node = ast.SimpleExpr() #has .term, which is an RValue type
        
        if self.current_token.tokentype in rvalueList:
            Expr_node.term = self.__rvalue() #returns an RValue
        else:
            self.__eat(token.LPAREN, "expected left parenthesis")
            Expr_node = self.__expr()
            self.__eat(token.RPAREN, "expected right parenthesis")
			
        if self.current_token.tokentype in mathrelList:
            ComplexExpr_node = ast.ComplexExpr()
            ComplexExpr_node.first_operand = Expr_node
            ComplexExpr_node.math_rel = self.__mathrel()
            ComplexExpr_node.rest = self.__expr()
            return ComplexExpr_node
        return Expr_node
			
    def __mathrel(self): #returns a token
        """<mathrel> ::= PLUS | MINUS | DIVIDE | MULTIPLY | MODULO"""
        theToken = self.current_token
        if self.current_token.tokentype == token.PLUS:
            self.__eat(token.PLUS, "expected plus sign")
        elif self.current_token.tokentype == token.MINUS:
            self.__eat(token.MINUS, "expected minus sign")
        elif self.current_token.tokentype == token.DIVIDE:
            self.__eat(token.DIVIDE, "expected division sign")
        elif self.current_token.tokentype == token.MULTIPLY:
            self.__eat(token.MULTIPLY, "expected multiplication sign")
        elif self.current_token.tokentype == token.MODULO:
            self.__eat(token.MODULO, "expected modulo sign")
        return theToken
			
    def __rvalue(self): #returns either simple, new, call, or IDRValue
        """<rvalue> ::= STRINGVAL | INTVAL | BOOLVAL | FLOATVAL | NIL | NEW ID | <idrval>"""
        theVal = self.current_token
        SimpleRValue_node = ast.SimpleRValue()
        NewRValue_node = ast.NewRValue()
        CallRValue_node = ast.CallRValue()
		
        if self.current_token.tokentype == token.STRINGVAL:
            self.__eat(token.STRINGVAL, "expected string value")
            SimpleRValue_node.val = theVal
            return SimpleRValue_node
        elif self.current_token.tokentype == token.INTVAL:
            self.__eat(token.INTVAL, "expected integer value")
            SimpleRValue_node.val = theVal
            return SimpleRValue_node
        elif self.current_token.tokentype == token.BOOLVAL:
            self.__eat(token.BOOLVAL, "expected boolean value")
            SimpleRValue_node.val = theVal
            return SimpleRValue_node
        elif self.current_token.tokentype == token.FLOATVAL:
            self.__eat(token.FLOATVAL, "expected float value")
            SimpleRValue_node.val = theVal
            return SimpleRValue_node
        elif self.current_token.tokentype == token.NIL:
            self.__eat(token.NIL, "expected nil")
            SimpleRValue_node.val = theVal
            return SimpleRValue_node
        elif self.current_token.tokentype == token.NEW:
            self.__eat(token.NEW, "expected new")
            NewRValue_node.struct_type = self.current_token
            self.__eat(token.ID, "expected identifier")
            return NewRValue_node
        else:
            theReturn = self.__idrval() #returns either IDRVal or CallRValue?
            return theReturn
		
    def __idrval(self): #returns either IDRVal or CallRValue but how does it determine?
        """<idrval> ::= ID (DOT ID)* | ID LPAREN <exprlist> RPAREN"""
        CallRValue_node = ast.CallRValue()
        IDRvalue_node = ast.IDRvalue()
        
        CallRValue_node.fun = self.current_token
        IDRvalue_node.path.append(self.current_token)

        self.__eat(token.ID, "expected identifier")
        if self.current_token.tokentype == token.DOT:
            while self.current_token.tokentype == token.DOT:
                self.__eat(token.DOT, "expected a dot")
                IDRvalue_node.path.append(self.current_token)
                self.__eat(token.ID, "expected identifier")
        elif self.current_token.tokentype == token.LPAREN:
            self.__eat(token.LPAREN, "expected left parenthesis")
            CallRValue_node.args = self.__exprlist() #returns a list of expressions
            self.__eat(token.RPAREN, "expected right parenthesis")
            return CallRValue_node
        return IDRvalue_node
			
    def __exprlist(self): #returns a list of expr
        """<exprlist> ::= <expr> ( COMMA <expr> )* | E"""
        expressionList = [token.LPAREN, token.PLUS, token.MINUS, token.DIVIDE, token.MULTIPLY,
        token.MODULO, token.STRINGVAL, token.INTVAL, token.BOOLVAL, token.FLOATVAL, token.NIL,
        token.NEW, token.ID]
        theExprList = [] #Just going to return a list of expressions thus we just append the
                         #expressions we receive into the list and return that
		
        if self.current_token.tokentype in expressionList:
            theExprList.append(self.__expr())
            while self.current_token.tokentype == token.COMMA:
                self.__eat(token.COMMA, "expected a comma")
                theExprList.append(self.__expr())
        return theExprList
				
    def __bexpr(self): #returns a BoolExpr node
        #self.first_expr = None # Expr node
        #self.bool_rel = None # Token (==, <=, !=, etc.)
        #self.second_expr = None # Expr node
        #self.bool_connector = None # Token (AND or OR)
        #self.rest = None # BoolExpr node
        #self.negated = False # Bool
        """<bexpr> ::= <expr> <bexprt> | NOT <bexpr> <bexprt> | LPAREN <bexpr> RPAREN <bconnct>"""
        BoolExpr_node = ast.BoolExpr()
		
        if self.current_token.tokentype == token.NOT:
            self.__eat(token.NOT, "Expected a not statement")
            BoolExpr_node = self.__bexpr()
            BoolExpr_node.negated = True
            self.__bexprt(BoolExpr_node)
            return BoolExpr_node
        elif self.current_token.tokentype == token.LPAREN:
            self.__eat(token.LPAREN, "Expected left parenthesis")
            BoolExpr_node = self.__bexpr()
            self.__eat(token.RPAREN, "Expected right parenthesis")
            if self.current_token.tokentype == token.OR or self.current_token.tokentype == token.AND:
                OuterBoolExpr_node = ast.BoolExpr()
                OuterBoolExpr_node.first_expr = BoolExpr_node
                self.__bconnct(OuterBoolExpr_node)
                return OuterBoolExpr_node
            return BoolExpr_node
        else:
            BoolExpr_node.first_expr = self.__expr()
            self.__bexprt(BoolExpr_node) #sets bool_rel, second_expr, bool_connector (which sets rest)
            return BoolExpr_node
            

		
    def __bexprt(self, BoolExpr_node): #completes the BoolExpr
        """<bexprt> ::= <boolrel> <expr> <bconnct> | <bconnct>"""
        boolList = [token.EQUAL, token.LESS_THAN, token.GREATER_THAN, token.LESS_THAN_EQUAL,
        token.GREATER_THAN_EQUAL, token.NOT_EQUAL]

        if self.current_token.tokentype in boolList:
            BoolExpr_node.bool_rel = self.__boolrel()
            BoolExpr_node.second_expr = self.__expr()
            self.__bconnct(BoolExpr_node)
        else:
            self.__bconnct(BoolExpr_node)
			
    def __bconnct(self, BoolExpr_node):
        myToken = self.current_token
        if self.current_token.tokentype == token.AND:
            self.__eat(token.AND, "expected an and")
            BoolExpr_node.rest = self.__bexpr()
            BoolExpr_node.bool_connector = myToken
        elif self.current_token.tokentype == token.OR:
            self.__eat(token.OR, "expected an or")
            BoolExpr_node.rest = self.__bexpr()
            BoolExpr_node.bool_connector = myToken
			
    def __boolrel(self): #returns Token (==, <=, !=, etc.)
        myToken = self.current_token
		
        if self.current_token.tokentype == token.EQUAL:
            self.__eat(token.EQUAL, "expected an equal")
        if self.current_token.tokentype == token.LESS_THAN:
            self.__eat(token.LESS_THAN, "expected a less than")
        if self.current_token.tokentype == token.GREATER_THAN:
            self.__eat(token.GREATER_THAN, "expected a greater than")
        if self.current_token.tokentype == token.LESS_THAN_EQUAL:
            self.__eat(token.LESS_THAN_EQUAL, "expected an equal")
        if self.current_token.tokentype == token.GREATER_THAN_EQUAL:
            self.__eat(token.GREATER_THAN_EQUAL, "expected a greater than equal")
        if self.current_token.tokentype == token.NOT_EQUAL:
            self.__eat(token.NOT_EQUAL, "expected a not equal")
        return myToken #perhaps flawed?
	