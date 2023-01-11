import numpy as np
import matplotlib.pyplot as plt

count_rankings = np.loadtxt("relative_counts.txt")
top_counts = count_rankings[:3]
count_rankings = count_rankings[3:]

plt.figure(figsize=(3.2, 8))

plt.plot(np.zeros_like(top_counts), top_counts, 'o', c=(
    0.3607, 0.082, 0.5137), mfc=(1, 0.7529, 0), mew=2.5, ms=10.0),
plt.plot(np.zeros_like(count_rankings), count_rankings, 'o', c=(
    0.3607, 0.082, 0.5137, 0.8), mfc=(0.8706, 0.831, 0.8862), mew=0.3),


# hide y-axis
ax = plt.gca()
ax.get_xaxis().set_visible(False)

plt.title('Relative Count Distribution')

plt.show()
