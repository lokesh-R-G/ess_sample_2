import ast
import operator
import math

class SafeEvaluator(ast.NodeVisitor):
    def __init__(self, context):
        self.context = context
        self.operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.USub: operator.neg,
            ast.Gt: operator.gt,
            ast.Lt: operator.lt,
            ast.GtE: operator.ge,
            ast.LtE: operator.le,
            ast.Eq: operator.eq,
            ast.NotEq: operator.ne
        }
        self.functions = {
            'Round': round,
            'Ceil': math.ceil,
            'Floor': math.floor,
            'Min': min,
            'Max': max,
            'IF': lambda cond, true_val, false_val: true_val if cond else false_val
        }

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        op = self.operators.get(type(node.op))
        if not op:
            raise ValueError(f"Unsupported operator: {type(node.op)}")
        return op(left, right)

    def visit_UnaryOp(self, node):
        operand = self.visit(node.operand)
        op = self.operators.get(type(node.op))
        if not op:
            raise ValueError(f"Unsupported unary operator: {type(node.op)}")
        return op(operand)

    def visit_Compare(self, node):
        left = self.visit(node.left)
        # Handle simple single comparisons
        right = self.visit(node.comparators[0])
        op = self.operators.get(type(node.ops[0]))
        if not op:
            raise ValueError(f"Unsupported comparison: {type(node.ops[0])}")
        return op(left, right)

    def visit_Call(self, node):
        func_name = node.func.id
        if func_name not in self.functions:
            raise ValueError(f"Unsupported function: {func_name}")
        args = [self.visit(arg) for arg in node.args]
        return self.functions[func_name](*args)

    def visit_Name(self, node):
        var_name = node.id
        if var_name in self.functions:
            return var_name
        if var_name not in self.context:
            raise ValueError(f"Missing context variable: {var_name}")
        return self.context[var_name]

    def visit_Constant(self, node):
        return node.value

    def generic_visit(self, node):
        raise ValueError(f"Unsupported syntax node: {type(node).__name__}")

class FormulaEngine:
    @staticmethod
    def evaluate(expression: str, context: dict) -> float:
        try:
            tree = ast.parse(expression, mode='eval')
            evaluator = SafeEvaluator(context)
            return float(evaluator.visit(tree.body))
        except Exception as e:
            raise ValueError(f"Formula evaluation failed for '{expression}': {str(e)}")
