import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import tensorflow as tf
from tensorflow.keras.models import load_model, Model
from tensorflow.keras.layers import Dense, Flatten, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ReduceLROnPlateau, EarlyStopping


categories = ['B', 'C', 'O', 'T', 'W']
num_classes = len(categories)

train_data_dir = "training_set"

base_model = load_model("1017model.h5")

for layer in base_model.layers[:int(len(base_model.layers) * 0.5)]:
    layer.trainable = False

base_model_output = base_model.layers[-2].output

x = Flatten(name="new_flatten")(base_model_output)
x = Dense(512, activation='relu', name="new_dense1")(x)
x = BatchNormalization(name="new_batchnorm1")(x)  # 归一化层，防止梯度爆炸
x = Dropout(0.5, name="new_dropout")(x)  # 增加 Dropout
x = Dense(256, activation='relu', name="new_dense2")(x)
x = BatchNormalization(name="new_batchnorm2")(x)
x = Dense(num_classes, activation='softmax', name="output_layer")(x)

new_model = Model(inputs=base_model.input, outputs=x)

new_model.compile(optimizer=Adam(learning_rate=0.0001), loss='categorical_crossentropy', metrics=['accuracy'])

train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=15,
    width_shift_range=0.2,
    height_shift_range=0.2,
    zoom_range=0.3,
    shear_range=0.2,
    horizontal_flip=True,
    brightness_range=[0.7, 1.3],
    validation_split=0.2
)


train_generator = train_datagen.flow_from_directory(
    train_data_dir,
    target_size=(224, 224),
    batch_size=64,
    class_mode='categorical',
    classes=categories,
    subset="training"
)

val_generator = train_datagen.flow_from_directory(
    train_data_dir,
    target_size=(224, 224),
    batch_size=64,
    class_mode='categorical',
    classes=categories,
    subset="validation"
)

lr_scheduler = ReduceLROnPlateau(monitor="val_accuracy", factor=0.5, patience=3, min_lr=1e-6)

early_stopping = EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True)


history = new_model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=40,
    steps_per_epoch=len(train_generator),
    validation_steps=len(val_generator),
    callbacks=[lr_scheduler, early_stopping]
)

new_model.save("fine_tuned_model.h5")
print(" 迁移学习完成，新模型已保存！")

