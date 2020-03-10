# Author: Maximillian Marciel
# Description:
# Full Implementation of a myPL interpreter
#----------------------------------------------------------------------

import mypl_token as token
import mypl_ast as ast
import mypl_error as error
import mypl_symbol_table as sym_tbl

class ReturnException(Exception): pass

class Interpreter(ast.Visitor):
    """A MyPL interpret visitor implementation"""
    #-----------------------------------------------------------------------------------
    
    def __init__(self):
        # initialize the symbol table (for ids -> values)
        self.sym_table = sym_tbl.SymbolTable()
        # holds the type of last expression type
        self.current_value = None
        # the heap {oid:struct_obj}
        self.heap = {}
        
    #-----------------------------------------------------------------------------------
        
    def run(self, stmt_list):
        try:
            stmt_list.accept(self)
        except ReturnException: #Why is the syntax invalid?
            pass
    
    #-----------------------------------------------------------------------------------
    
    def __error(self, msg, the_token):
        raise error.MyPLError(msg, int(the_token.line), int(the_token.column))
        
    #-----------------------------------------------------------------------------------
        
    def visit_stmt_list(self, stmt_list):
        self.sym_table.push_environment()
        for stmt in stmt_list.stmts:
            stmt.accept(self)
        self.sym_table.pop_environment()
        
    #-----------------------------------------------------------------------------------
        
    def visit_expr_stmt(self, expr_stmt):
        #self.expr = None # Expr node
        expr_stmt.expr.accept(self)
        
    #-----------------------------------------------------------------------------------
        
    def visit_assign_stmt(self, assign_stmt):
        #self.lhs = None # LValue node
        #self.rhs = None # Expr node
        #self.sym_table.set_info(identifier, self.current_value)
        
        assign_stmt.rhs.accept(self)
        assign_stmt.lhs.accept(self)
        #rhs_val = self.current_value
        #assign_stmt.lhs = rhs_val
        #self.sym_table.set_info(assign_stmt.lhs.path[0].lexeme, rhs_val)
        
        
    #-----------------------------------------------------------------------------------    
        
    def visit_return_stmt(self, return_stmt):
        #self.return_expr = None # Expr
        #self.return_token = None # to keep track of location (e.g., return;)
        
        #...set current val to return expression
        if return_stmt.return_expr is not None:
            return_stmt.return_expr.accept(self)
        else:
            self.current_value = None
        raise ReturnException()
        
    #-----------------------------------------------------------------------------------  
    
    def visit_while_stmt(self, while_stmt):
        #self.bool_expr = None # a BoolExpr node
        #self.stmt_list = StmtList()

        #push/pop environment already done by statement list
        while_stmt.bool_expr.accept(self)
        while self.current_value is True:
            while_stmt.stmt_list.accept(self)
            while_stmt.bool_expr.accept(self)
    
    #----------------------------------------------------------------------------------- 
    
    def visit_if_stmt(self, if_stmt):
        #self.if_part = BasicIf()
        #self.elseifs = [] # list of BasicIf
        #self.has_else = False
        #self.else_stmts = StmtList()
        
        #BasicIf:
        #self.bool_expr = None # BoolExpr node
        #self.stmt_list = StmtList()
        ifWasTrue = False
        
        
        if_stmt.if_part.bool_expr.accept(self)
        if self.current_value == True:
            ifWasTrue = True
            self.sym_table.push_environment()
            if_stmt.if_part.stmt_list.accept(self)
            self.sym_table.pop_environment()
        
        elifWasTrue = False
        
        i = 0
        #Only executes if it has else ifs, if no previous else if was true, and if the above if was false.
        while (i < len(if_stmt.elseifs)) and (elifWasTrue == False) and (ifWasTrue == False):
            if_stmt.elseifs[i].bool_expr.accept(self)
            if self.current_value == True:
                elifWasTrue = True
                self.sym_table.push_environment()
                if_stmt.elseifs[i].stmt_list.accept(self)
                self.sym_table.pop_environment()
            i += 1
            
        #Only executes if no else if is true, and if the if statement itself was false.
        if (if_stmt.has_else == True) and (elifWasTrue == False) and (ifWasTrue == False):
            self.sym_table.push_environment()
            if_stmt.else_stmts.accept(self)
            self.sym_table.pop_environment()
            
    #-----------------------------------------------------------------------------------
    
    def visit_simple_expr(self, simple_expr):
        #self.term = None # RValue
        if simple_expr.term is not None:
            simple_expr.term.accept(self)
            
    #-----------------------------------------------------------------------------------
    
    def visit_complex_expr(self, complex_expr):
        #self.first_operand = None # Expr node
        #self.math_rel = None # Token (+, -, *, etc.)
        #self.rest = None # Expr node
        """<mathrel> ::= PLUS | MINUS | DIVIDE | MULTIPLY | MODULO"""
        complex_expr.first_operand.accept(self)
        first_op = self.current_value
        complex_expr.rest.accept(self)
        rest_op  = self.current_value
        
        if complex_expr.math_rel.tokentype == token.PLUS:
            if (not isinstance(first_op, str)) and isinstance(rest_op, str):
                self.current_value = str(first_op) + rest_op
            elif isinstance(first_op, str) and (not isinstance(first_op, str)):
                self.current_value = first_op + str(rest_op)
            else:
                self.current_value = first_op + rest_op
        elif complex_expr.math_rel.tokentype == token.MINUS:
            self.current_value = first_op - rest_op
        elif complex_expr.math_rel.tokentype == token.DIVIDE:
            if isinstance(first_op, int) and isinstance(rest_op, int): #integer division
                self.current_value = first_op // rest_op
            else:
                self.current_value = first_op / rest_op
        elif complex_expr.math_rel.tokentype == token.MULTIPLY:
            self.current_value = first_op * rest_op
        elif complex_expr.math_rel.tokentype == token.MODULO:
            self.current_value = first_op % rest_op
     
    #-----------------------------------------------------------------------------------
    
    def visit_bool_expr(self, bool_expr):
        #self.first_expr = None # Expr node
        #self.bool_rel = None # Token (==, <=, !=, etc.)
        #self.second_expr = None # Expr node
        #self.bool_connector = None # Token (AND or OR)
        #self.rest = None # BoolExpr node
        #self.negated = False # Bool
        #(first_val == second_val) && rest,   for example.
        
        #Evaluating the values for first, second, val.
        bool_expr.first_expr.accept(self)
        first_val = self.current_value
        if bool_expr.second_expr is not None:
            bool_expr.second_expr.accept(self)
            second_val = self.current_value
        if bool_expr.rest is not None:
            bool_expr.rest.accept(self)
            rest_val = self.current_value
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        if bool_expr.second_expr is not None:
            if bool_expr.bool_rel.tokentype == token.EQUAL:
                temp_val = (first_val == second_val)
            elif bool_expr.bool_rel.tokentype == token.GREATER_THAN:
                temp_val = (first_val > second_val)
            elif bool_expr.bool_rel.tokentype == token.GREATER_THAN_EQUAL:
                temp_val = (first_val >= second_val)
            elif bool_expr.bool_rel.tokentype == token.LESS_THAN:
                temp_val = (first_val < second_val)
            elif bool_expr.bool_rel.tokentype == token.LESS_THAN_EQUAL:
                temp_val = (first_val <= second_val)
            elif bool_expr.bool_rel.tokentype == token.NOT_EQUAL:
                temp_val = (first_val != second_val)
        else:
            temp_val = first_val
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #Evaluating the rest
        if bool_expr.rest is not None:
            if bool_expr.bool_connector.tokentype == token.AND:
                final_val = temp_val and rest_val
            elif bool_expr.bool_connector.tokentype == token.OR:
                final_val = temp_val or rest_val
        else:
            final_val = temp_val
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #print(first_val, " ", bool_expr.bool_rel.lexeme, " ", second_val, " is ", final_val)
        self.current_value = final_val
        
        
    #-----------------------------------------------------------------------------------
        
    def visit_simple_rvalue(self, simple_rvalue):
        if simple_rvalue.val.tokentype == token.INTVAL:
            self.current_value = int(simple_rvalue.val.lexeme)
        elif simple_rvalue.val.tokentype == token.FLOATVAL:
            self.current_value = float(simple_rvalue.val.lexeme)
        elif simple_rvalue.val.tokentype == token.BOOLVAL:
            self.current_value = True
        if simple_rvalue.val.lexeme == 'false':
            self.current_value = False
        elif simple_rvalue.val.tokentype == token.STRINGVAL:
            self.current_value = simple_rvalue.val.lexeme
        elif simple_rvalue.val.tokentype == token.NIL:
            self.current_value = None
            
    #-----------------------------------------------------------------------------------
            
    def visit_var_decl_stmt(self, var_decl):
        #self.var_id = None # Token (ID)
        #self.var_type = None # Token (STRINGTYPE, ..., ID)
        #self.var_expr = None # Expr node
        var_decl.var_expr.accept(self)
        exp_value = self.current_value
        var_name = var_decl.var_id.lexeme
        self.sym_table.add_id(var_decl.var_id.lexeme)
        self.sym_table.set_info(var_decl.var_id.lexeme, exp_value)
        
    #-----------------------------------------------------------------------------------
        
    def __built_in_fun_helper(self, call_rvalue):
        #self.fun = None # Token (id)
        #self.args = [] # list of Expr
        fun_name = call_rvalue.fun.lexeme
        arg_vals = []
        """Built ins: length(str), get(int, str), print(str),
           reads(str), readi(int), itos(int), ftos(float), itof(int)"""
        
        #... evaluate each call argument and store in arg_vals ...
        i = 0
        while i < len(call_rvalue.args):
            call_rvalue.args[i].accept(self)
            arg_vals.append(self.current_value)
            i += 1
            
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # check for nil values
        for i, arg in enumerate(arg_vals):
            if arg is None:
                msg = "Nil value error"
                self.__error(msg, call_rvalue.fun)
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # perform each function
        if fun_name == 'print':
            if isinstance(arg_vals[0], str):
                arg_vals[0] = arg_vals[0].replace(r'\n','\n')
            print(arg_vals[0], end='')
        elif fun_name == 'length':
            self.current_value = len(arg_vals[0])
        elif fun_name == 'get':
            if 0 <= arg_vals[0] < len(arg_vals[1]):
                self.current_value = arg_vals[1][arg_vals[0]]
            else:
                msg = "Index out of range"
                self.error(msg, call_rvalue.fun)
        elif fun_name == 'reads':
            self.current_value = input()
        elif fun_name == 'readi':
            try:
                self.current_value = int(input())
            except ValueError:
                self.__error('bad int value', call_rvalue.fun)
        elif fun_name == 'readf':
            try:
                self.current_value = float(input())
            except ValueError:
                self.__error('bad float value', call_rvalue.fun)
        elif fun_name == 'itos':
            self.current_value = str(arg_vals[0])
        elif fun_name == 'ftos':
            self.current_value = str(arg_vals[0])
        elif fun_name == 'itof':
            self.current_value = float(arg_vals[0])
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    #-----------------------------------------------------------------------------------
    
    def visit_struct_decl_stmt(self, struct_decl):
        #self.struct_id = None # Token (id)
        #self.var_decls = [] # [VarDeclStmt]
        
        self.sym_table.add_id(struct_decl.struct_id.lexeme) #Is this right?
        env_id = self.sym_table.get_env_id()
        self.sym_table.set_info(struct_decl.struct_id.lexeme, [env_id, struct_decl])
        
    #-----------------------------------------------------------------------------------
        
    def visit_fun_decl_stmt(self, fun_decl):
        #self.fun_name = None # Token (id)
        #self.params = [] # List of FunParam
        #self.return_type = None # Token
    
        self.sym_table.add_id(fun_decl.fun_name.lexeme) #is this right?
        env_id = self.sym_table.get_env_id()
        self.sym_table.set_info(fun_decl.fun_name.lexeme, [env_id, fun_decl])
        
    #-----------------------------------------------------------------------------------
        
    def visit_lvalue(self, lval):
        #self.path = [] # [Token (ID)] ... one implies simple var

        identifier = lval.path[0].lexeme
        if len(lval.path) == 1:
            self.sym_table.set_info(identifier, self.current_value)
            #struct_dict = self.sym_table.get_info(identifier)
            #self.current_value = struct_dict[identifier]
        else:
            #... handle path expressions ...
            last = self.sym_table.get_info(lval.path[0].lexeme)
            i = 1
            while i < len(lval.path): #iterates through the path
                struct_dict = self.heap[last]
                path_id = lval.path[i].lexeme
                last = struct_dict[path_id]

                if i == len(lval.path) - 1: #if at last spot
                    #put current val into it (into what?)
                    struct_dict[path_id] = self.current_value
                i += 1
               
    #-----------------------------------------------------------------------------------
        
    def visit_fun_param(self, fun_param):
        pass
        #Do nothing here
        
    #-----------------------------------------------------------------------------------
            
    def visit_new_rvalue(self, new_rvalue):
        #self.struct_type = None # Token (id)
        
        struct_info = self.sym_table.get_info(new_rvalue.struct_type.lexeme)
        
        #save current env, and go to struct env
        curr_env = self.sym_table.get_env_id()
        self.sym_table.set_env_id(struct_info[0])
        
        #create empty struct obj, init vars, reset env
        struct_obj = {}
        self.sym_table.push_environment()
        
        #... initialize struct_obj w/ vars in struct_info[1] ...
        i = 0
        while i < len(struct_info[1].var_decls):
            struct_info[1].var_decls[i].var_expr.accept(self)
            struct_obj[struct_info[1].var_decls[i].var_id.lexeme] = self.current_value
            i += 1
        self.sym_table.pop_environment()
        
        #... return to starting environment
        self.sym_table.set_env_id(curr_env)
        
        #create the oid, add struct to heap, assign cur val
        oid = id(struct_obj)
        self.heap[oid] = struct_obj
        self.current_value = oid

        
    #-----------------------------------------------------------------------------------
            
    def visit_call_rvalue(self, call_rvalue):
        #self.fun = None # Token (id)
        #self.args = [] # list of Expr
    
        # handle built in functions first
        built_ins = ['print', 'length', 'get', 'readi', 'reads',
                     'readf', 'itof', 'itos', 'ftos', 'stoi', 'stof']
        if call_rvalue.fun.lexeme in built_ins:
            self.__built_in_fun_helper(call_rvalue)
        else:
            #... handle user-defined function calls ...
            
            #get the function information
            fun_info = self.sym_table.get_info(call_rvalue.fun.lexeme)
            #Structure: [env_id, fun_decl]
            
            #store the current environment
            curr_env = self.sym_table.get_env_id()
            
            #compute and store the argument vals
            i = 0
            argVals = []
            while i < len(call_rvalue.args):
                call_rvalue.args[i].accept(self)
                argVals.append(self.current_value)
                i += 1
            
            #go to the function declarations env
            self.sym_table.set_env_id(fun_info[0])
            
            #add a new environment (for the function to run in)
            self.sym_table.push_environment()
            
            #initialize params with the argument values
            fun_decl = fun_info[1]
            i = 0
            while i < len(fun_decl.params):
                self.sym_table.add_id(fun_decl.params[i].param_name.lexeme)
                self.sym_table.set_info(fun_decl.params[i].param_name.lexeme, argVals[i])
                i += 1
            
            #visit the functions statement list (need to catch return exceptions here)
            try:
                fun_decl.stmt_list.accept(self)
            except ReturnException:
                pass
            
            #remove the new environment
            self.sym_table.pop_environment()
            
            #return to the caller's environment
            self.sym_table.set_env_id(curr_env)
            
    #-----------------------------------------------------------------------------------
            
    def visit_id_rvalue(self, id_rvalue):
        #self.path = [] # List of Token (id)
        last  = self.sym_table.get_info(id_rvalue.path[0].lexeme)
        i = 1
        for path_id in id_rvalue.path[1:]:
            struct_obj = self.heap[last] #struct_obj = look in heap
            path_id = id_rvalue.path[i].lexeme
            last = struct_obj[path_id]
            i += 1
        self.current_value = last
    #-----------------------------------------------------------------------------------
            
            
            
            
            
            
            
            
            
            
            
            

