import numpy as np
from scipy.misc import derivative


def partial_derivative(func, arr, dx=1e-6):
    """计算n元函数在某点各个自变量的梯度向量（偏导数列表）

    :param func: [function] n元函数
    :param arr: [list/tuple] 目标点的自变量坐标
    :param dx: [int/float] 计算时x的增量
    :return: [list] 偏导数
    """
    n_features = len(arr)
    ans = []
    for i in range(n_features):
        def f(x):
            arr2 = list(arr)
            arr2[i] = x
            return func(arr2)

        ans.append(derivative(f, arr[i], dx=dx))
    return ans


def get_hessian(func, x0, dx=1e-6):
    """计算n元函数在某点的黑塞矩阵

    :param func: [function] n元函数
    :param x0: [list/tuple] 目标点的自变量坐标
    :param dx: [int/float] 计算时x的增量
    :return: [list] 黑塞矩阵
    """
    n_features = len(x0)
    ans = [[0] * n_features for _ in range(n_features)]
    for i in range(n_features):
        def f1(xi, x1):
            x2 = list(x1)
            x2[i] = xi
            return func(x2)

        for j in range(n_features):
            # 当x[j]=xj时，x[i]方向的斜率
            def f2(xj):
                x1 = list(x0)
                x1[j] = xj
                res = derivative(f1, x0=x1[i], dx=dx, args=(x1,))
                return res

            ans[i][j] = derivative(f2, x0[j], dx=dx)

    return ans


def golden_section_for_line_search(func, a0, b0, epsilon):
    """一维搜索极小值点（黄金分割法）

    :param func: [function] 一元函数
    :param a0: [int/float] 目标区域左侧边界
    :param b0: [int/float] 目标区域右侧边界
    :param epsilon: [int/float] 精度
    """
    a1, b1 = a0 + 0.382 * (b0 - a0), b0 - 0.382 * (b0 - a0)
    fa, fb = func(a1), func(b1)

    while b1 - a1 > epsilon:
        if fa <= fb:
            b0, b1, fb = b1, a1, fa
            a1 = a0 + 0.382 * (b0 - a0)
            fa = func(a1)
        else:
            a0, a1, fa = a1, b1, fb
            b1 = b0 - 0.382 * (b0 - a0)
            fb = func(b1)

    return (a1 + b1) / 2


def bfgs_algorithm(func, n_features, epsilon=1e-6, distance=3, maximum=1000):
    """BFGS算法

    :param func: [function] n元目标函数
    :param n_features: [int] 目标函数元数
    :param epsilon: [int/float] 学习精度
    :param distance: [int/float] 每次一维搜索的长度范围（distance倍梯度的模）
    :param maximum: [int] 最大学习次数
    :return: [list] 结果点坐标
    """
    B0 = np.identity(n_features)  # 构造初始矩阵G0(单位矩阵)
    x0 = [0] * n_features  # 取初始点x0

    for k in range(maximum):
        # 计算梯度 gk
        nabla = partial_derivative(func, x0)
        g0 = np.matrix([nabla]).T  # g0 = g_k

        # 当梯度的模长小于精度要求时，停止迭代
        if pow(sum([nabla[i] ** 2 for i in range(n_features)]), 0.5) < epsilon:
            return x0

        # 计算pk
        if k == 0:
            pk = - B0 * g0  # 若numpy计算逆矩阵时有0，则对应位置会变为inf
        else:
            pk = - (B0 ** -1) * g0

        # 一维搜索求lambda_k
        def f(x):
            """pk 方向的一维函数"""
            x2 = [x0[j] + x * float(pk[j][0]) for j in range(n_features)]
            return func(x2)

        lk = golden_section_for_line_search(f, 0, distance, epsilon=1e-6)  # lk = lambda_k

        # 更新当前点坐标
        x1 = [x0[j] + lk * float(pk[j][0]) for j in range(n_features)]

        # 计算g_{k+1}，若模长小于精度要求时，则停止迭代
        nabla = partial_derivative(func, x1)
        g1 = np.matrix([nabla]).T  # g0 = g_{k+1}

        # 当梯度的模长小于精度要求时，停止迭代
        if pow(sum([nabla[i] ** 2 for i in range(n_features)]), 0.5) < epsilon:
            return x1

        # 计算G_{k+1}
        yk = g1 - g0
        dk = np.matrix([[lk * float(pk[j][0]) for j in range(n_features)]]).T

        B1 = B0 + (yk * yk.T) / (yk.T * dk) + (B0 * dk * dk.T * B0) / (dk.T * B0 * dk)

        B0 = B1
        x0 = x1


if __name__ == "__main__":
    # [0]
    print(bfgs_algorithm(lambda x: x[0] ** 2, 1, epsilon=1e-6))

    # [-3.0000000003324554, -3.9999999998511546]
    print(bfgs_algorithm(lambda x: ((x[0] + 3) ** 2 + (x[1] + 4) ** 2) / 2, 2, epsilon=1e-6))
