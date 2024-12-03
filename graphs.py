import matplotlib
import matplotlib.pyplot as plt

# TEST
x = [1, 2, 3, 4, 5, 6]
y = [4, 7, 9, 2, 7, 2]

fig, ax = plt.subplots()
ax.plot(x,y)
ax.set_xlabel('test x')
ax.set_ylabel('test y')
ax.grid()
fig.savefig('test.png')
plt.show()