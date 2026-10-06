# CMPSC 202 - Midterm Programming Assignment

Name: Issei Hasegawa

**Instructions**: Complete the exercise below. Open book, open notes, any tools allowed (except submitting another student's work). Due tonight (10/6) at 11:59pm.

**Submission**: Fork this repository and invite your professor (username: bcmullins) to the repository. To submit, push your code to your forked repository. Make sure to include your name in the README file.

You have been provided with a starter Python file (`midterm_starter.py`). This file contains two fully implemented algorithms that solve the exact same problem: finding if an array contains duplicate values.

The file also contains a `flawed_benchmark()` function. The developer who wrote this benchmark made several severe methodological errors, making the printed timing results completely unreliable for comparing the asymptotic growth of these two algorithms.

**Your tasks**: 

1. Rewrite the `flawed_benchmark()` function to provide a robust empirical comparison of the two algorithms. List the methodological errors in the original benchmark and explain how you fixed them. Your benchmark should demonstrate the scaling behavior of the two algorithms across multiple input sizes.

   1. The original benchmark only tested one input size (n = 1000). With only one data point, it is impossible to tell how the running time grows as the input gets larger, which is the whole point of comparing an O(n^2) algorithm with an O(n) one. I changed the benchmark to run both algorithms on eight different sizes (250, 500, 1000, 1500, 2000, 3000, 4000, and 5000) so the growth can be seen in the plot.

   2. The timer was started before the input list was created, so the time it took to build the list was included in the measured time. Creating the list takes O(n) time on its own, so this adds extra time that has nothing to do with the algorithm, and it hides the difference between the two algorithms, especially for the fast one. I now generate the input first and only start the timer right before calling the algorithm and stop it right after.

   3. The two algorithms were given different random lists (data1 and data2). Since the inputs were not the same, the comparison was not fair. For example, one list might have a duplicate near the beginning and the other near the end. In my version, one list is generated for each trial and both algorithms get a copy of that same list.

   4. The way the input was generated, random.randint(i, 10000), almost always produces duplicates. Both algorithms return True as soon as they find the first duplicate, so most of the time they stop early and never do their full amount of work. This means the measured time depends on where the first duplicate happens to be rather than on n. Also, when n is larger than 10001, the lower bound i becomes bigger than 10000 and randint raises a ValueError, so the benchmark cannot even run for larger sizes. To fix this, I used random.sample(range(10 * n), n), which gives n distinct numbers. Since there are no duplicates, both algorithms have to check the entire list, which is the worst case, so the times reflect O(n^2) and O(n).

   5. time.time() measures wall-clock time and its resolution can be too coarse for very short runs. The fast algorithm finishes in microseconds, so the measurement can be inaccurate. time.time() can also be affected if the system clock is adjusted. I replaced it with time.perf_counter(), which has a higher resolution and is meant for measuring short time intervals.

   6. Each algorithm was only run once. A single run can be affected by other processes on the computer, caching, or garbage collection, so one measurement is not reliable. I now run 7 trials for each input size and use the median, which is less affected by outliers than the average. I also turned off garbage collection during the timing, did a warm-up run before the real measurements, and alternated the order of the two algorithms in each trial so that neither one always runs first.

   7. No random seed was set, so the input data and the results were different every time the program ran. I added random.seed(202) at the start so the results can be reproduced.

   8. The original code only printed two numbers, so there was no way to see a trend. My version stores the median time for each size and plots both algorithms in results.png. The plot has a normal (linear) scale graph and a log-log graph. On the log-log graph, I added reference lines with slope 2 and slope 1. The slow algorithm follows the slope 2 line and the fast algorithm follows the slope 1 line, which matches O(n^2) and O(n).

2. Run the empirical comparion and plot the results using a plotting library of your choice (e.g., `matplotlib`, `seaborn`, etc.). Include the plot in your submission called `results.png`. Be sure to label your axes and include a legend.

   ![Benchmark results](results.png)

   The results match the expected growth rates. From n = 500 on, every time n doubles, the slow algorithm takes about 4 times longer (for example, 0.0062 s at n = 1000 and 0.0256 s at n = 2000), while the fast algorithm only takes about 2 times longer (0.000027 s at n = 1000 and 0.000058 s at n = 2000). This is what we expect from O(n^2) and O(n). The jump from 250 to 500 is about 5 times for the slow algorithm, which I think is because the runs at n = 250 only take about 0.0003 s and are easily affected by noise.

   The log-log graph makes this easier to see. On a log-log plot, a function like n^k shows up as a straight line with slope k. When I fit a line to the measured times, the slope was about 2.1 for the slow algorithm and about 1.0 for the fast algorithm, and both lines follow the reference lines in the plot. On the linear graph, the fast algorithm looks almost flat because it is so much faster. At n = 5000, the slow algorithm took 0.163 s and the fast algorithm took 0.00018 s, which is about 900 times faster, and this gap keeps growing as n gets larger.



