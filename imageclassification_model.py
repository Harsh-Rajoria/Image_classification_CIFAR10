# -*- coding: utf-8 -*-
"""Imageclassification_Model.ipynb

Original file is located at
    https://colab.research.google.com/drive/1uRMZY0q-OBM8ECTPStX71EfEikuGrcEX
"""

import tensorflow as tf
from tensorflow.keras import layers, models
import matplotlib.pyplot as plt
import numpy as np

class ImageClassifier:
    def __init__(self, img_height=32, img_width=32):
        self.img_height = img_height
        self.img_width = img_width
        self.model = None
        self.history = None
        self.class_names = ['airplane', 'automobile', 'bird', 'cat', 'deer',
                           'dog', 'frog', 'horse', 'ship', 'truck']

    def load_cifar10(self):
        """Load and preprocess CIFAR-10 dataset"""
        # Load the dataset
        (x_train, y_train), (x_test, y_test) = tf.keras.datasets.cifar10.load_data()

        # Normalize pixel values to be between 0 and 1
        x_train = x_train.astype('float32') / 255.0
        x_test = x_test.astype('float32') / 255.0

        # Convert class vectors to binary class matrices
        y_train = tf.keras.utils.to_categorical(y_train, 10)
        y_test = tf.keras.utils.to_categorical(y_test, 10)

        return (x_train, y_train), (x_test, y_test)

    def build_model(self):
        """Create a CNN model architecture"""
        model = models.Sequential([
            # First Convolutional Block
            layers.Conv2D(32, (3, 3), padding='same', input_shape=(32, 32, 3)),
            layers.BatchNormalization(),
            layers.Activation('relu'),
            layers.Conv2D(32, (3, 3), padding='same'),
            layers.BatchNormalization(),
            layers.Activation('relu'),
            layers.MaxPooling2D(pool_size=(2, 2)),
            layers.Dropout(0.25),

            # Second Convolutional Block
            layers.Conv2D(64, (3, 3), padding='same'),
            layers.BatchNormalization(),
            layers.Activation('relu'),
            layers.Conv2D(64, (3, 3), padding='same'),
            layers.BatchNormalization(),
            layers.Activation('relu'),
            layers.MaxPooling2D(pool_size=(2, 2)),
            layers.Dropout(0.25),

            # Dense Layers
            layers.Flatten(),
            layers.Dense(512),
            layers.BatchNormalization(),
            layers.Activation('relu'),
            layers.Dropout(0.5),
            layers.Dense(10, activation='softmax')
        ])

        optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)


        model.compile(
            optimizer=optimizer,
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )

        self.model = model
        return model

    def train(self, x_train, y_train, x_test, y_test, epochs=100, batch_size=64):
        """Train the model"""
        if self.model is None:
            raise ValueError("Model not built. Call build_model first.")

        # Data augmentation
        datagen = tf.keras.preprocessing.image.ImageDataGenerator(
            rotation_range=15,
            width_shift_range=0.1,
            height_shift_range=0.1,
            horizontal_flip=True
        )
        datagen.fit(x_train)

        # Train with data augmentation
        self.history = self.model.fit(
            datagen.flow(x_train, y_train, batch_size=batch_size),
            epochs=epochs,
            validation_data=(x_test, y_test),
            callbacks=[
                tf.keras.callbacks.EarlyStopping(
                    monitor='val_loss',
                    patience=5,
                    restore_best_weights=True
                )
            ]
        )

    def plot_training_history(self):
        """Plot training history"""
        if self.history is None:
            raise ValueError("No training history available.")

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

        # Plot accuracy
        ax1.plot(self.history.history['accuracy'])
        ax1.plot(self.history.history['val_accuracy'])
        ax1.set_title('Model Accuracy')
        ax1.set_ylabel('Accuracy')
        ax1.set_xlabel('Epoch')
        ax1.legend(['Train', 'Validation'])

        # Plot loss
        ax2.plot(self.history.history['loss'])
        ax2.plot(self.history.history['val_loss'])
        ax2.set_title('Model Loss')
        ax2.set_ylabel('Loss')
        ax2.set_xlabel('Epoch')
        ax2.legend(['Train', 'Validation'])

        plt.tight_layout()
        plt.show()

    def display_sample_predictions(self, x_test, y_test, num_images=5):
        """Display sample predictions"""
        predictions = self.model.predict(x_test)
        fig, axes = plt.subplots(1, num_images, figsize=(15, 3))

        for i in range(num_images):
            axes[i].imshow(x_test[i])
            pred_label = self.class_names[np.argmax(predictions[i])]
            true_label = self.class_names[np.argmax(y_test[i])]
            color = 'green' if pred_label == true_label else 'red'
            axes[i].set_title(f'Pred: {pred_label}\nTrue: {true_label}', color=color)
            axes[i].axis('off')

        plt.tight_layout()
        plt.show()

    def evaluate(self, x_test, y_test):
        """Evaluate the model and print detailed metrics"""
        test_loss, test_accuracy = self.model.evaluate(x_test, y_test, verbose=0)
        predictions = self.model.predict(x_test)
        y_pred = np.argmax(predictions, axis=1)
        y_true = np.argmax(y_test, axis=1)

        # Print evaluation metrics
        print(f"\nTest Accuracy: {test_accuracy:.4f}")
        print(f"Test Loss: {test_loss:.4f}")

        # Print per-class accuracy
        for i in range(10):
            mask = y_true == i
            class_acc = np.mean(y_pred[mask] == y_true[mask])
            print(f"Accuracy for {self.class_names[i]}: {class_acc:.4f}")

# Create and train the model
classifier = ImageClassifier()

# Load CIFAR-10 dataset
(x_train, y_train), (x_test, y_test) = classifier.load_cifar10()

# Build and train the model
classifier.build_model()
classifier.train(x_train, y_train, x_test, y_test)

#save the model
classifier.model.save('my_cifar10_model.h5')

# Visualize results
classifier.plot_training_history()
classifier.display_sample_predictions(x_test, y_test)

# Evaluate the model
classifier.evaluate(x_test, y_test)

