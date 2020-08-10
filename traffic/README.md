# Traffic

Traffic is a python app for identifying traffic signs.

## Convolution process

With two times of convolution, each time has a convolutional layer and a max-pooling layer.
Then, flatten it.

## Hidden Layer

A hidden layer with 128 neurons and a dropout layer with rate 0.3.

## Output layer

Finally, an output layer with 43(number of categories) neurons.

## Experimentation process

First, I tried to the same model as the lecture's model for MNIST except for the image size and output neurons, but it gave me only 5% accuracy. Then, I tried adding one more convolutional layer and the accuracy climbed to 92%. Finally, I lowered the dropout rate from 0.5 to 0.3, and got this better accuracy.

## Dataset

gtsrb - German Traffic Sign Benchmarks

# Reference

https://cs50.harvard.edu/ai/2020/projects/5/traffic/
