#Maximillian Marciel
#mypl_type_checker.py
#2/26/19

import mypl_token as token
import mypl_ast as ast
import mypl_error as error
import mypl_symbol_table as symbol_table

class TypeChecker(ast.Visitor):

    #The typechecker is commented out because it was incomplete and gave false errors,
    #interfering with the completion of assignment 6.
    
    """A MyPL type checker visitor implementation where struct types
    take the form: type_id -> {v1:t1, ..., vn:tn} and function types
    take the form: fun_id -> [[t1, t2, ..., tn,], return_type]
    """
    pass
    
    """def __init__(self):
        # initialize the symbol table (for ids -> types)
        self.sym_table = symbol_table.SymbolTable()
        # current_type holds the type of the last expression type
        self.current_type = None
        # global env (for return)
        self.sym_table.push_environment()
        # set global return type to int
        self.sym_table.add_id('return')
        self.sym_table.set_info('return', token.INTTYPE)
        # load in built-in function types
        self.sym_table.add_id('print')
        self.sym_table.set_info('print', [[token.STRINGTYPE], token.NIL])
        self.sym_table.add_id('length')
        self.sym_table.set_info('length', token.INTTYPE)
        self.sym_table.add_id('get')
        self.sym_table.set_info('get', token.STRINGTYPE)
        self.sym_table.add_id('itof')
        self.sym_table.set_info('itof', token.FLOATTYPE)
        self.sym_table.add_id('itos')
        self.sym_table.set_info('itos', token.STRINGTYPE)
        self.sym_table.add_id('ftos')
        self.sym_table.set_info('ftos', token.STRINGTYPE)
        self.sym_table.add_id('reads')
        self.sym_table.set_info('reads', token.STRINGTYPE)
        self.sym_table.add_id('readi')
        self.sym_table.set_info('readi', token.INTTYPE)
        
    def __error(self, error_msg, token):
        s = error_msg
        l = token.line
        c = token.column
        raise error.MyPLError(s, int(l), int(c))
        
    
    def visit_stmt_list(self, stmt_list):
        # add new block (scope)
        self.sym_table.push_environment()
        for stmt in stmt_list.stmts:
            stmt.accept(self)
        # remove new block
        self.sym_table.pop_environment()
        
    def visit_expr_stmt(self, expr_stmt):
        expr_stmt.expr.accept(self)
        
    def visit_var_decl_stmt(self, var_decl):
        #self.var_id = None # Token (ID)
        #self.var_type = None # Token (STRINGTYPE, ..., ID)
        #self.var_expr = None # Expr node
        self.sym_table.add_id(var_decl.var_id.lexeme)
        if var_decl.var_type is not None: #If it's explicit, the type is what it says
            if var_decl.var_type.tokentype is token.ID:
                self.sym_table.set_info(var_decl.var_id.lexeme, var_decl.var_type.lexeme)
            else:
                self.sym_table.set_info(var_decl.var_id.lexeme, var_decl.var_type.tokentype)
            
            #self.sym_table.set_info(var_decl.var_id.lexeme, var_decl.var_type.tokentype) #change this
            #check if it's an ID. if it's an ID grab the lexeme not the tokentype
            
        var_decl.var_expr.accept(self)
        exprType = self.current_type
        
        if var_decl.var_type is None: #If it's implicit, the type is whatever is on right
            self.sym_table.set_info(var_decl.var_id.lexeme, exprType)
            
        if var_decl.var_type is not None: #If there's a mismatch between the explicit type
            if (var_decl.var_type.tokentype != exprType):
                if (var_decl.var_type.lexeme != exprType):
                    if exprType != token.NIL:
                        msg = 'Mismatched type in explicit variable declaration'
                        self.__error(msg, var_decl.var_id)
                    
        
    def visit_assign_stmt(self, assign_stmt):
        #self.lhs = None # LValue node
        #self.rhs = None # Expr node
        assign_stmt.rhs.accept(self)
        rhs_type = self.current_type
        assign_stmt.lhs.accept(self)
        lhs_type = self.current_type
        if rhs_type != token.NIL and rhs_type != lhs_type:
            msg = 'mismatch type in assignment'
            self.__error(msg, assign_stmt.lhs.path[0])
    
    def visit_struct_decl_stmt(self, struct_decl):
        #self.struct_id = None # Token (id)
        #self.var_decls = [] # [VarDeclStmt]
        self.sym_table.add_id(struct_decl.struct_id.lexeme)
        self.sym_table.push_environment()
        structType = {}
        i = 0
        while i < len(struct_decl.var_decls):
            struct_decl.var_decls[i].accept(self)
            structType[struct_decl.var_decls[i].var_id.lexeme] = self.sym_table.get_info(struct_decl.var_decls[i].var_id.lexeme)       
            i += 1
        self.sym_table.pop_environment()
        self.sym_table.set_info(struct_decl.struct_id.lexeme, structType)
        
    def visit_fun_decl_stmt(self, fun_decl):
        #self.fun_name = None # Token (id)
        #self.params = [] # List of FunParam
        #self.return_type = None # Token
        #self.stmt_list = StmtList() # StmtList
        #---------------------------------------
        self.sym_table.add_id(fun_decl.fun_name.lexeme)
        self.sym_table.set_info(fun_decl.fun_name.lexeme, [[],]) #set as empty initially, set info before pushing
        self.sym_table.push_environment()
        self.sym_table.add_id('return')
        self.sym_table.set_info('return', fun_decl.return_type)
        paramList = []
        i = 0
        while i < len(fun_decl.params): #is this correct
            fun_decl.params[i].accept(self)
            paramList.append(self.current_type)
            i += 1
        fun_decl.stmt_list.accept(self)
        self.sym_table.pop_environment()
        finalList = [paramList, fun_decl.return_type.tokentype]
        self.sym_table.set_info(fun_decl.fun_name.lexeme, finalList)
        
    def visit_return_stmt(self, return_stmt):
        #self.return_expr = None # Expr
        #self.return_token = None # to keep track of location (e.g., return;)
        if return_stmt.return_expr is not None:
            return_stmt.return_expr.accept(self)
            returnType = self.current_type
        
    def visit_while_stmt(self, while_stmt):
        #self.bool_expr = None # a BoolExpr node
        #self.stmt_list = StmtList()
        self.sym_table.push_environment()
        while_stmt.bool_expr.accept(self)
        while_stmt.stmt_list.accept(self)
        self.sym_table.pop_environment()
        
    def visit_if_stmt(self, if_stmt):
        #self.if_part = BasicIf()
        #self.elseifs = [] # list of BasicIf
        #self.has_else = False
        #self.else_stmts = StmtList()
        
        self.sym_table.push_environment()
        if_stmt.if_part.bool_expr.accept(self)
        if_stmt.if_part.stmt_list.accept(self)
        self.sym_table.pop_environment()
        i = 0
        while i < len(if_stmt.elseifs):
            self.sym_table.push_environment()
            if_stmt.elseifs[i].bool_expr.accept(self)
            if_stmt.elseifs[i].stmt_list.accept(self)
            self.sym_table.pop_environment()
            i += 1
        self.sym_table.push_environment()
        if_stmt.else_stmts.accept(self)
        self.sym_table.pop_environment()
        
    def visit_simple_expr(self, simple_expr):
        #self.expr = None # Expr node
        if simple_expr.term is not None:
            simple_expr.term.accept(self)
        
    def visit_complex_expr(self, complex_expr):
        #self.first_operand = None # Expr node
        #self.math_rel = None # Token (+, -, *, etc.)
        #self.rest = None # Expr node
        complex_expr.first_operand.accept(self)
        firstOp_type = self.current_type
        complex_expr.rest.accept(self)
        restOp_type = self.current_type
        if firstOp_type != token.NIL:
            if firstOp_type != restOp_type:
                msg = 'Mismatched type in expression'
                self.__error(msg, complex_expr.math_rel)
        self.current_type = restOp_type
        
    def visit_bool_expr(self, bool_expr):
        #self.first_expr = None # Expr node
        #self.bool_rel = None # Token (==, <=, !=, etc.)
        #self.second_expr = None # Expr node
        #self.bool_connector = None # Token (AND or OR)
        #self.rest = None # BoolExpr node
        #self.negated = False # Bool
          
        bool_expr.first_expr.accept(self)
        firstExp_type = self.current_type
        if bool_expr.second_expr is not None:
            bool_expr.second_expr.accept(self)
            secondExp_type = self.current_type
        if bool_expr.rest is not None:
            bool_expr.rest.accept(self)
            rest_type = self.current_type
        if (bool_expr.second_expr is not None) and (bool_expr.rest is not None):
            if firstExp_type != secondExp_type != rest_type:
                msg = 'Mismatched type in boolean expression'
                self.__error(msg, bool_expr.bool_rel)
            
        
        
    def visit_lvalue(self, lval):
        #self.path = [] # [Token (ID)] ... one implies simple var
        #When you declare a struct, you Say that the name of the struct is put onto the symbol table
        #its type is the type of its member vars
        
        if not self.sym_table.id_exists(lval.path[0].lexeme):
            msg = 'Use before def error in id, first right value'
            self.__error(msg, lval.path[0])
        last_type = self.sym_table.get_info(lval.path[0].lexeme)
        i = 1
        while i < len(lval.path):
            if not self.sym_table.id_exists(last_type):
                msg = 'Use before declaration of member variable'
                self.__error(msg, id_rvalue.path[i])
            struct_type = self.sym_table.get_info(last_type) #struct_Type is the dictionary
            path_id = lval.path[i].lexeme
            if not path_id in struct_type:
                msg = 'Use before declaration of member variable'
                self.__error(msg, id_rvalue.path[i])
            last_type = struct_type[path_id]
            i += 1
        
        self.current_type = last_type
  
    def visit_fun_param(self, fun_param):
        #self.param_name = None # Token (id)
        #self.param_type = None # Token (id)
        self.sym_table.add_id(fun_param.param_name.lexeme)
        self.sym_table.set_info(fun_param.param_name.lexeme, fun_param.param_type.tokentype)
        self.current_type = fun_param.param_type.tokentype
        
    def visit_simple_rvalue(self, simple_rvalue):
        #self.val = None # Token
        if simple_rvalue.val.tokentype == token.INTVAL:
            self.current_type = token.INTTYPE
        if simple_rvalue.val.tokentype == token.BOOLVAL:
            self.current_type = token.BOOLTYPE
        if simple_rvalue.val.tokentype == token.FLOATVAL:
            self.current_type = token.FLOATTYPE
        if simple_rvalue.val.tokentype == token.STRINGVAL:
            self.current_type = token.STRINGTYPE
        if simple_rvalue.val.tokentype == token.NIL:
            self.current_type = token.NIL
        
    def visit_new_rvalue(self, new_rvalue):
        #self.struct_type = None # Token (id)
        if not self.sym_table.id_exists(new_rvalue.struct_type.lexeme):
            msg = 'Use before declaration in new'
            self.__error(msg, new_rvalue.struct_type)
            
        if new_rvalue.struct_type.tokentype is token.ID:
            self.current_type = new_rvalue.struct_type.lexeme
        else:
            self.current_type = new_rvalue.struct_type.tokentype
        #self.current_type = new_rvalue.struct_type.tokentype
        
    def visit_call_rvalue(self, call_rvalue):
        #self.fun = None # Token (id)
        #self.args = [] # list of Expr

        #Checking to see if it exists first
        if not self.sym_table.id_exists(call_rvalue.fun.lexeme):
            msg = 'Use before declaration in function call'
            self.__error(msg, call_rvalue.fun)
        
        #Of structure [ [params, params2, ..], return_type]
        funType = self.sym_table.get_info(call_rvalue.fun.lexeme)
        paramList = funType[0]
        
        #Evaluating parameters (If there are any)
        if paramList:
            i = 0
            while i < len(call_rvalue.args):
                call_rvalue.args[i].accept(self)
                argsType = self.current_type
                if (argsType is not paramList[i]):
                    if paramList[i] is token.NIL:
                        msg = 'Parameters do not match function declaration in call'
                        self.__error(msg, call_rvalue.fun)
                i += 1
            self.current_type = funType[1]
        
        
    def visit_id_rvalue(self, id_rvalue):
        #self.path = [] # List of Token (id)
        if not self.sym_table.id_exists(id_rvalue.path[0].lexeme):
            msg = 'Use before def error in id, first right value'
            self.__error(msg, id_rvalue.path[0])
        last_type = self.sym_table.get_info(id_rvalue.path[0].lexeme)
        last_lexeme = id_rvalue.path[0].lexeme
        i = 1
        while i < len(id_rvalue.path):
            if not self.sym_table.id_exists(last_type):
                msg = 'Use before declaration of member variable'
                self.__error(msg, id_rvalue.path[i])
            struct_type = self.sym_table.get_info(last_type) #struct_Type is the dictionary
            path_id = id_rvalue.path[i].lexeme
            if not path_id in struct_type:
                msg = 'Use before declaration of member variable'
                self.__error(msg, id_rvalue.path[i])
            last_type = struct_type[path_id]
            i += 1
        
        self.current_type = last_type"""
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   