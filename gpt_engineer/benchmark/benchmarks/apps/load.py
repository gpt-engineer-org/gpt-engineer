"""
Module for loading APPS evaluation tasks.

This module provides functionality to load tasks for evaluating GPT-based models
on smaller, more focused tasks. It defines a set of tasks with predefined prompts
and assertions to benchmark the performance of AI models.

Functions
---------
load_apps : function
    Loads the APPS benchmark, which consists of a series coding problems.
"""
from gpt_engineer.benchmark.types import Benchmark, Task
from gpt_engineer.core.files_dict import FilesDict


def load_apps():
    """
    Loads the APPS benchmark, which consists of a series coding problems.

    Returns
    -------
    Benchmark
        A Benchmark object containing a list of Task objects for the APPS evaluation.
    """
    return Benchmark(
        name="APPS",
        tasks=[
            Task(
                name="2361",
                initial_code=FilesDict({"main.py": ""}),
                command="python main.py",
                prompt="You are given an array $a$ of length $n$ consisting of zeros. You perform $n$ actions with this array: during the $i$-th action, the following sequence of operations appears: Choose the maximum by length subarray (continuous subsegment) consisting only of zeros, among all such segments choose the leftmost one; Let this segment be $[l; r]$. If $r-l+1$ is odd (not divisible by $2$) then assign (set) $a[\frac{l+r}{2}] := i$ (where $i$ is the number of the current action), otherwise (if $r-l+1$ is even) assign (set) $a[\frac{l+r-1}{2}] := i$. Consider the array $a$ of length $5$ (initially $a=[0, 0, 0, 0, 0]$). Then it changes as follows: Firstly, we choose the segment $[1; 5]$ and assign $a[3] := 1$, so $a$ becomes $[0, 0, 1, 0, 0]$; then we choose the segment $[1; 2]$ and assign $a[1] := 2$, so $a$ becomes $[2, 0, 1, 0, 0]$; then we choose the segment $[4; 5]$ and assign $a[4] := 3$, so $a$ becomes $[2, 0, 1, 3, 0]$; then we choose the segment $[2; 2]$ and assign $a[2] := 4$, so $a$ becomes $[2, 4, 1, 3, 0]$; and at last we choose the segment $[5; 5]$ and assign $a[5] := 5$, so $a$ becomes $[2, 4, 1, 3, 5]$. Your task is to find the array $a$ of length $n$ after performing all $n$ actions. Note that the answer exists and unique. You have to answer $t$ independent test cases. -----Input----- The first line of the input contains one integer $t$ ($1 \le t \le 10^4$) — the number of test cases. Then $t$ test cases follow. The only line of the test case contains one integer $n$ ($1 \le n \le 2 \cdot 10^5$) — the length of $a$. It is guaranteed that the sum of $n$ over all test cases does not exceed $2 \cdot 10^5$ ($\sum n \le 2 \cdot 10^5$). -----Output----- For each test case, print the answer — the array $a$ of length $n$ after performing $n$ actions described in the problem statement. Note that the answer exists and unique. -----Example----- Input 6 1 2 3 4 5 6 Output 1 1 2 2 1 3 3 1 2 4 2 4 1 3 5 3 4 1 5 2 6",
                input='6\n1\n2\n3\n4\n5\n6\n',
                assertions={
                     "correct output": lambda assertable: '1 \n1 2 \n2 1 3 \n3 1 2 4 \n2 4 1 3 5 \n3 4 1 5 2 6 \n'.replace(' ', '') in assertable.stdout.replace(' ', ''),
                },
            ),
            Task(
                name="2362",
                initial_code=FilesDict({"main.py": ""}),
                command="python main.py",
                prompt="$n$ robots have escaped from your laboratory! You have to find them as soon as possible, because these robots are experimental, and their behavior is not tested yet, so they may be really dangerous! Fortunately, even though your robots have escaped, you still have some control over them. First of all, you know the location of each robot: the world you live in can be modeled as an infinite coordinate plane, and the $i$-th robot is currently located at the point having coordinates ($x_i$, $y_i$). Furthermore, you may send exactly one command to all of the robots. The command should contain two integer numbers $X$ and $Y$, and when each robot receives this command, it starts moving towards the point having coordinates ($X$, $Y$). The robot stops its movement in two cases: either it reaches ($X$, $Y$); or it cannot get any closer to ($X$, $Y$). Normally, all robots should be able to get from any point of the coordinate plane to any other point. Each robot usually can perform four actions to move. Let's denote the current coordinates of the robot as ($x_c$, $y_c$). Then the movement system allows it to move to any of the four adjacent points: the first action allows it to move from ($x_c$, $y_c$) to ($x_c - 1$, $y_c$); the second action allows it to move from ($x_c$, $y_c$) to ($x_c$, $y_c + 1$); the third action allows it to move from ($x_c$, $y_c$) to ($x_c + 1$, $y_c$); the fourth action allows it to move from ($x_c$, $y_c$) to ($x_c$, $y_c - 1$). Unfortunately, it seems that some movement systems of some robots are malfunctioning. For each robot you know which actions it can perform, and which it cannot perform. You want to send a command so all robots gather at the same point. To do so, you have to choose a pair of integer numbers $X$ and $Y$ so that each robot can reach the point ($X$, $Y$). Is it possible to find such a point? -----Input----- The first line contains one integer $q$ ($1 \le q \le 10^5$) — the number of queries. Then $q$ queries follow. Each query begins with one line containing one integer $n$ ($1 \le n \le 10^5$) — the number of robots in the query. Then $n$ lines follow, the $i$-th of these lines describes the $i$-th robot in the current query: it contains six integer numbers $x_i$, $y_i$, $f_{i, 1}$, $f_{i, 2}$, $f_{i, 3}$ and $f_{i, 4}$ ($-10^5 \le x_i, y_i \le 10^5$, $0 \le f_{i, j} \le 1$). The first two numbers describe the initial location of the $i$-th robot, and the following four numbers describe which actions the $i$-th robot can use to move ($f_{i, j} = 1$ if the $i$-th robot can use the $j$-th action, and $f_{i, j} = 0$ if it cannot use the $j$-th action). It is guaranteed that the total number of robots over all queries does not exceed $10^5$. -----Output----- You should answer each query independently, in the order these queries appear in the input. To answer a query, you should do one of the following: if it is impossible to find a point that is reachable by all $n$ robots, print one number $0$ on a separate line; if it is possible to find a point that is reachable by all $n$ robots, print three space-separated integers on the same line: $1$ $X$ $Y$, where $X$ and $Y$ are the coordinates of the point reachable by all $n$ robots. Both $X$ and $Y$ should not exceed $10^5$ by absolute value; it is guaranteed that if there exists at least one point reachable by all robots, then at least one of such points has both coordinates not exceeding $10^5$ by absolute value. -----Example----- Input 4 2 -1 -2 0 0 0 0 -1 -2 0 0 0 0 3 1 5 1 1 1 1 2 5 0 1 0 1 3 5 1 0 0 0 2 1337 1337 0 1 1 1 1336 1337 1 1 0 1 1 3 5 1 1 1 1 Output 1 -1 -2 1 2 5 0 1 -100000 -100000",
                input="4\n2\n-1 -2 0 0 0 0\n-1 -2 0 0 0 0\n3\n1 5 1 1 1 1\n2 5 0 1 0 1\n3 5 1 0 0 0\n2\n1337 1337 0 1 1 1\n1336 1337 1 1 0 1\n1\n3 5 1 1 1 1\n",
                assertions={
                     "correct output": lambda assertable: "1 -1 -2\n1 2 5\n0\n1 -100000 -100000\n".replace(' ', '') in assertable.stdout.replace(' ', ''),
                },
            ),
            Task(
                name="2363",
                initial_code=FilesDict({"main.py": ""}),
                command="python main.py",
                prompt="There are $n$ athletes in front of you. Athletes are numbered from $1$ to $n$ from left to right. You know the strength of each athlete — the athlete number $i$ has the strength $s_i$. You want to split all athletes into two teams. Each team must have at least one athlete, and each athlete must be exactly in one team. You want the strongest athlete from the first team to differ as little as possible from the weakest athlete from the second team. Formally, you want to split the athletes into two teams $A$ and $B$ so that the value $|\max(A) - \min(B)|$ is as small as possible, where $\max(A)$ is the maximum strength of an athlete from team $A$, and $\min(B)$ is the minimum strength of an athlete from team $B$. For example, if $n=5$ and the strength of the athletes is $s=[3, 1, 2, 6, 4]$, then one of the possible split into teams is: first team: $A = [1, 2, 4]$, second team: $B = [3, 6]$. In this case, the value $|\max(A) - \min(B)|$ will be equal to $|4-3|=1$. This example illustrates one of the ways of optimal split into two teams. Print the minimum value $|\max(A) - \min(B)|$. -----Input----- The first line contains an integer $t$ ($1 \le t \le 1000$) — the number of test cases in the input. Then $t$ test cases follow. Each test case consists of two lines. The first line contains positive integer $n$ ($2 \le n \le 50$) — number of athletes. The second line contains $n$ positive integers $s_1, s_2, \ldots, s_n$ ($1 \le s_i \le 1000$), where $s_i$ — is the strength of the $i$-th athlete. Please note that $s$ values may not be distinct. -----Output----- For each test case print one integer — the minimum value of $|\max(A) - \min(B)|$ with the optimal split of all athletes into two teams. Each of the athletes must be a member of exactly one of the two teams. -----Example----- Input 5 5 3 1 2 6 4 6 2 1 3 2 4 3 4 7 9 3 1 2 1 1000 3 100 150 200 Output 1 0 2 999 50 -----Note----- The first test case was explained in the statement. In the second test case, one of the optimal splits is $A=[2, 1]$, $B=[3, 2, 4, 3]$, so the answer is $|2-2|=0$.",
                input="5\n5\n3 1 2 6 4\n6\n2 1 3 2 4 3\n4\n7 9 3 1\n2\n1 1000\n3\n100 150 200\n",
                assertions={
                     "correct output": lambda assertable: "1\n0\n2\n999\n50\n".replace(' ', '') in assertable.stdout.replace(' ', ''),
                },
            ),
        ],
    )
