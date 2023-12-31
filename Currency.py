#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import gradio as gr
import matplotlib.pyplot as plt
import numpy as np
import os
import PIL
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential
import pathlib


# In[ ]:


# Load and preprocess the dataset
data_dir = 'Data'
data_dir = pathlib.Path(data_dir)

ten = list(data_dir.glob('ten/*'))
print(ten[0])
PIL.Image.open(str(ten[0]))

img_height, img_width = 180, 180
batch_size = 32

train_ds = tf.keras.preprocessing.image_dataset_from_directory(
    data_dir,
    validation_split=0.2,
    subset="training",
    seed=123,
    image_size=(img_height, img_width),
    batch_size=batch_size
)

val_ds = tf.keras.preprocessing.image_dataset_from_directory(
    data_dir,
    validation_split=0.2,
    subset="validation",
    seed=123,
    image_size=(img_height, img_width),
    batch_size=batch_size
)

class_names = train_ds.class_names
print(class_names)


# In[ ]:


# Visualize some sample images
plt.figure(figsize=(10, 10))
for images, labels in train_ds.take(1):
    for i in range(9):
        ax = plt.subplot(3, 3, i + 1)
        plt.imshow(images[i].numpy().astype("uint8"))
        plt.title(class_names[labels[i]])
        plt.axis("off")


# In[ ]:


# Build and train the model
num_classes = len(class_names)

model = Sequential([
    layers.experimental.preprocessing.Rescaling(1./255, input_shape=(img_height, img_width, 3)),
    layers.Conv2D(16, 3, padding='same', activation='relu'),
    layers.MaxPooling2D(),
    layers.Conv2D(32, 3, padding='same', activation='relu'),
    layers.MaxPooling2D(),
    layers.Conv2D(64, 3, padding='same', activation='relu'),
    layers.MaxPooling2D(),
    layers.Flatten(),
    layers.Dense(128, activation='relu'),
    layers.Dense(num_classes, activation='softmax')
])

model.compile(optimizer='adam',
              loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
              metrics=['accuracy'])

epochs = 50
history = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=epochs
)


# In[ ]:


# Define the prediction function
def predict_image(img):
    img_4d = img.reshape(-1, 180, 180, 3)
    prediction = model.predict(img_4d)[0]
    class_index = np.argmax(prediction)
    confidence = prediction[class_index]
    return class_names[class_index], confidence


# In[ ]:


# Set up Gradio Interface
image = gr.Image(shape=(180, 180))
label = gr.Label(num_top_classes=1)

gr.Interface(fn=predict_image, inputs=image, outputs=label, interpretation='default').launch(share=True)

