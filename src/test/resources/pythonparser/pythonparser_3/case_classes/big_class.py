# Copyright Aniskov N.

import ast
import operator


def is_same_op(op1, op2):
    if isinstance(op1, (ast.Add, ast.Sub)) and isinstance(op2, (ast.Add, ast.Sub)):
        return True

    if isinstance(op1, (ast.Mult, ast.Div)) and isinstance(op2, (ast.Mult, ast.Div)):
        return True

    return False


def get_same_op(op):
    if isinstance(op, (ast.Add, ast.Sub)):
        return ast.Add

    if isinstance(op, (ast.Mult, ast.Div)):
        return ast.Mult

    return False


class ConstantOptimizer(ast.NodeTransformer):
    # mapping ast operators to "action" operators
    _ast_op_to_action_op = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.MatMult: operator.matmul,
        ast.Div: operator.truediv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.LShift: operator.lshift,
        ast.RShift: operator.rshift,
        ast.BitOr: operator.or_,
        ast.BitXor: operator.xor,
        ast.BitAnd: operator.and_,
        ast.FloorDiv: operator.floordiv,
    }

    @staticmethod
    def _common_value_getter(const_like_instance):
        instance_class = const_like_instance.__class__

        if (instance_class is ast.Constant) or (instance_class is ast.NameConstant):
            return const_like_instance.value

        elif instance_class is ast.Num:
            return const_like_instance.n

        elif (instance_class is ast.Str) or (instance_class is ast.Bytes):
            return const_like_instance.s

        else:
            assert False, 'Unexpected behavior!'  # or Exception

    def visit(self, node):
        ast.NodeTransformer.generic_visit(self, node)

        if not isinstance(node, ast.BinOp):
            return node

        left = node.left
        right = node.right
        op = node.op
        op_action = self._ast_op_to_action_op[op.__class__]

        const_like_types = (ast.Constant, ast.Num, ast.Str, ast.NameConstant, ast.Bytes)
        if isinstance(left, const_like_types) and isinstance(right, const_like_types):
            left_val = ConstantOptimizer._common_value_getter(left)
            right_val = ConstantOptimizer._common_value_getter(right)
            return ast.Constant(value=op_action(left_val, right_val))

        # Handles expressions such as:
        # '1 * x' -> 'x',
        # '0 * x' -> '0',
        # '1 * (2 + x)' -> (2 + x),
        # '1 ** x' -> 1,
        # ...
        elif isinstance(left, const_like_types):

            left_val = ConstantOptimizer._common_value_getter(left)

            if left_val == 0:
                if isinstance(op, ast.Mult) or isinstance(op, ast.Pow):
                    return ast.Constant(value=0)

                elif isinstance(op, ast.Add):
                    return right

            elif left_val == 1:
                if isinstance(op, ast.Mult):
                    return right

                elif isinstance(op, ast.Pow):
                    return ast.Constant(value=1)

            elif isinstance(right, ast.BinOp) and is_same_op(op, right.op) and isinstance(right.op, (ast.Add, ast.Mult)):
                left_val = ConstantOptimizer._common_value_getter(left)
                right_val = ConstantOptimizer._common_value_getter(right.left)
                return ast.BinOp(op=get_same_op(op), left=op_action(left_val, right_val), right=right.right)

            return node

        # The same as previous one,
        # but with 1 or 0 on the right side of the expression
        # Handles expressions such as:
        # 'x * 1' -> 'x',
        # 'x * 0' -> '0',
        # '(2 + x) * 1' -> '(2 + x)',
        # 'x ** 1' -> 'x',
        # 'x << 0' -> 'x',
        # 'x >> 0' -> 'x'
        # ...
        elif isinstance(right, const_like_types):
            right_val = ConstantOptimizer._common_value_getter(right)

            if right_val == 0:
                if isinstance(op, ast.Mult):
                    return ast.Constant(value=0)

                elif isinstance(op, (ast.Add, ast.LShift, ast.RShift)):
                    return left

                elif isinstance(op, ast.Pow):
                    return ast.Constant(value=1)

            elif right_val == 1:
                if isinstance(op, (ast.Mult, ast.Pow)):
                    return left

                elif isinstance(op, ast.Pow):
                    return ast.Constant(value=1)

            elif isinstance(left, ast.BinOp) and is_same_op(op, left.op) and isinstance(left.op, (ast.Add, ast.Mult)):
                left_val = ConstantOptimizer._common_value_getter(left.left)
                right_val = ConstantOptimizer._common_value_getter(right)
                return ast.BinOp(op=get_same_op(op), left=op_action(left_val, right_val), right=left.right)

            if isinstance(op, (ast.Add, ast.Mult)):
                node.left, node.right = right, left

            return node

        else:
            if not isinstance(op, (ast.Add, ast.Sub, ast.Mult, ast.Div)):
                return node
            if isinstance(left, ast.BinOp) and is_same_op(op, left.op) and isinstance(left.op, (ast.Add, ast.Mult)) \
               and isinstance(right, ast.BinOp) and is_same_op(op, right.op) and isinstance(right.op, (ast.Add, ast.Mult)):
                if isinstance(left.left, const_like_types) and isinstance(right.left, const_like_types):
                    left_val = ConstantOptimizer._common_value_getter(left.left)
                    right_val = ConstantOptimizer._common_value_getter(right.left)
                    return ast.BinOp(op=get_same_op(op), left=op_action(left_val, right_val), right=ast.BinOp(op=op, left=left.right, right=right.right))
                elif isinstance(left.left, const_like_types):
                    left_val = ConstantOptimizer._common_value_getter(left.left)
                    return ast.BinOp(op=get_same_op(op), left=left_val, right=ast.BinOp(op=op, left=left.right, right=right))
                elif isinstance(right.left, const_like_types):
                    right_val = ConstantOptimizer._common_value_getter(right.left)
                    return ast.BinOp(op=get_same_op(op), left=right_val, right=ast.BinOp(op=op, left=left, right=right.right))
            else:
                return node