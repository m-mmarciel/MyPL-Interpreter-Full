# Maximillian Marciel
# Pretty print visitor for the
# abstract syntax tree
# 2/14/19

import mypl_token as token
import mypl_ast as ast
import sys

class PrintVisitor(ast.Visitor):
    """An AST pretty printer"""
	
    def __init__(self, output_stream):
        self.indent = 0 # to increase/decrease indent level
        self.output_stream = output_stream # where printing to
		
    def __indent(self):
        """Get default indent of four spaces"""
        return '    ' * self.indent
		
    def __write(self, msg):
        self.output_stream.write(msg)
		
    def visit_stmt_list(self, stmt_list):
        for stmt in stmt_list.stmts:
            stmt.accept(self)
			
    def visit_expr_stmt(self, expr_stmt):
        self.__write(self.__indent())
        expr_stmt.expr.accept(self)
        self.__write(';\n')
		
    def visit_var_decl_stmt(self, var_decl):
        #self.var_id = None # Token (ID)
        #self.var_type = None # Token (STRINGTYPE, ..., ID)
        #self.var_expr = None # Expr node
        self.__write(self.__indent())
        self.__write('var ')
        #print(var_decl.var_id.lexeme, end=': ')
        self.__write(var_decl.var_id.lexeme)
        if var_decl.var_type is not None:
            self.__write(": ")
            self.__write(var_decl.var_type.lexeme)
        self.__write(" = ")
        var_decl.var_expr.accept(self)
        self.__write(';\n')
        
    def visit_assign_stmt(self, assign_stmt):
        #self.lhs = None # LValue node
        #self.rhs = None # Expr node
        self.__write(self.__indent())
        self.__write('set ')
        assign_stmt.lhs.accept(self)
        self.__write(' = ')
        assign_stmt.rhs.accept(self)
        self.__write(';\n')
		
    def visit_struct_decl_stmt(self, struct_decl):
        #self.struct_id = None # Token (id)
        #self.var_decls = [] # [VarDeclStmt]
        self.__write(self.__indent()) #not certain of this
        self.__write("struct ")
        self.__write(struct_decl.struct_id.lexeme)
        self.__write("\n")
        self.indent = self.indent + 1
		
        i = 0
        while i < len(struct_decl.var_decls):
            struct_decl.var_decls[i].accept(self)
            i += 1
			
        self.indent = self.indent - 1
        self.__write(self.__indent())
        self.__write("end\n\n")
		
    def visit_fun_decl_stmt(self, fun_decl): #Where do we go to write the body of the function?
        #self.fun_name = None # Token (id)
        #self.params = [] # List of FunParam
        #self.return_type = None # Token
        #self.stmt_list = StmtList() # StmtList
		
        self.__write(self.__indent())
        self.__write("fun ")
        self.__write(str(fun_decl.return_type.lexeme))
        self.__write(" ")
        self.__write(str(fun_decl.fun_name.lexeme))
        self.__write("(")
        i = 0
        while i < len(fun_decl.params): #idk why it's printing the second one first
            fun_decl.params[i].accept(self)
            if not i == (len(fun_decl.params) - 1):
                self.__write(", ")
            i += 1
        self.__write(")\n")
        self.indent = self.indent + 1
        fun_decl.stmt_list.accept(self)
        self.indent = self.indent - 1
        self.__write('end\n\n')
		
    def visit_fun_param(self, fun_param):
        #self.param_name = None # Token (id)
        #self.param_type = None # Token (id)
        self.__write(fun_param.param_name.lexeme)
        self.__write(": ")
        self.__write(fun_param.param_type.lexeme)
		
    def visit_return_stmt(self, return_stmt):
        #self.return_expr = None # Expr
        #self.return_token = None # to keep track of location (e.g., return;)
        self.__write(self.__indent())
        if return_stmt.return_expr is not None:
            self.__write("return ")
            return_stmt.return_expr.accept(self)
        else:
            self.__write("return")
        self.__write(";\n")
		
    def visit_simple_expr(self, simple_expr):
        #self.term = None # RValue
        if simple_expr.term is not None:
            simple_expr.term.accept(self)
		
    def visit_complex_expr(self, complex_expr):
        #self.first_operand = None # Expr node
        #self.math_rel = None # Token (+, -, *, etc.)
        #self.rest = None # Expr node
        self.__write("(")
        complex_expr.first_operand.accept(self)
        self.__write(" ")
        self.__write(complex_expr.math_rel.lexeme)
        self.__write(" ")
        complex_expr.rest.accept(self)
        self.__write(")")
		
    def visit_simple_rvalue(self, simple_rvalue):
        #self.val = None # Token
        if simple_rvalue.val.tokentype == token.STRINGVAL:
            self.__write('"')
        self.__write(simple_rvalue.val.lexeme)
        if simple_rvalue.val.tokentype == token.STRINGVAL:
            self.__write('"')

    def visit_lvalue(self, lval):
        #self.path = [] # [Token (ID)] ... one implies simple var
        i = 0
        while i < len(lval.path):
            self.__write(lval.path[i].lexeme)
            if len(lval.path) > 1:
                if i is not len(lval.path) - 1:
                    self.__write(".")
            i += 1

    def visit_new_rvalue(self, new_rvalue):
        #self.struct_type = None # Token (id)
        self.__write("new ")
        self.__write(new_rvalue.struct_type.lexeme)
		
    def visit_call_rvalue(self, call_rvalue):
        #self.fun = None # Token (id)
        #self.args = [] # list of Expr
        self.__write(call_rvalue.fun.lexeme)
        self.__write("(")
        i = 0
        while i < len(call_rvalue.args):
            call_rvalue.args[i].accept(self)
            i += 1
        self.__write(")")
        
    def visit_id_rvalue(self, id_rvalue):
        #self.path = [] # List of Token (id)
        i = 0
        while i < len(id_rvalue.path):
            self.__write(id_rvalue.path[i].lexeme)
            if i is not len(id_rvalue.path) - 1:
                self.__write(".")
            i += 1
        
        
    def visit_while_stmt(self, while_stmt):
        #self.bool_expr = None # a BoolExpr node
        #self.stmt_list = StmtList()
        self.__write(self.__indent())
        self.__write("while ")
        while_stmt.bool_expr.accept(self)
        self.__write(" do\n")
        self.indent += 1
        while_stmt.stmt_list.accept(self)
        self.indent -= 1
        self.__write(self.__indent())
        self.__write("end\n")
		
    def visit_bool_expr(self, bool_expr):
        #self.first_expr = None # Expr node
        #self.bool_rel = None # Token (==, <=, !=, etc.)
        #self.second_expr = None # Expr node
        #self.bool_connector = None # Token (AND or OR)
        #self.rest = None # BoolExpr node
        #self.negated = False # Bool
        
        if bool_expr.negated:
            self.__write("not ")
        if bool_expr.bool_connector is not None:
            self.__write("(")    
        if bool_expr.bool_rel is not None:
            self.__write("(")
        bool_expr.first_expr.accept(self)
        if bool_expr.bool_rel is not None:
            self.__write(" ")
            self.__write(bool_expr.bool_rel.lexeme)
            self.__write(" ")
            bool_expr.second_expr.accept(self)
            self.__write(")")
        if bool_expr.bool_connector is not None:
            self.__write(" ")
            self.__write(bool_expr.bool_connector.lexeme)
            self.__write(" ")
            bool_expr.rest.accept(self)
            self.__write(")")

    def visit_if_stmt(self, if_stmt):
        #self.if_part = BasicIf()
        #self.elseifs = [] # list of BasicIf
        #self.has_else = False
        #self.else_stmts = StmtList()
        self.__write(self.__indent())
        self.__write("if ")
        if_stmt.if_part.bool_expr.accept(self)
        self.__write(" then\n")
        self.indent = self.indent + 1
        if_stmt.if_part.stmt_list.accept(self)
        self.indent = self.indent - 1
        i = 0
        while i < len(if_stmt.elseifs):
            self.__write("elif ")
            if_stmt.elseifs[i].bool_expr.accept(self)
            self.__write(" then\n")
            self.indent = self.indent + 1
            if_stmt.elseifs[i].stmt_list.accept(self)
            self.indent = self.indent - 1
            i += 1
        if if_stmt.has_else:
            self.__write("else\n")
            self.indent = self.indent + 1
            if_stmt.else_stmts.accept(self)
            self.indent = self.indent - 1
        self.__write(self.__indent())
        self.__write("end\n")
        
        
        
        
        
        
        
        