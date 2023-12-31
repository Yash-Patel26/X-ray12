"""A script to save a Keras Model as a TensorFlow protobuf file"""

# General imports
import os
import argparse

# ML imports
from keras import backend as K
from keras.models import load_model
import tensorflow as tf
from tensorflow.python.framework import graph_util
from tensorflow.python.framework import graph_io

# Imports from our code
import models

def rename_outputs(model, output_name_prefix):
    """Renames the outputs of the provided model to follow the format: output_<i> for the ith output

    Args:
        model: keras.models.Model
            The Keras Model whose outputs should be renamed

    Returns:
        The list of generated output names
    """

    outputs = model.outputs
    output_names = []

    for i in range(len(outputs)):
        output_name = output_name_prefix + str(i)
        output_names.append(output_name) # Save the name in a list for later
        tf.identity(outputs[i], output_name) # Rename the operation in the TensorFlow graph

    return output_names

def export_to_pb(output_names, output_model_path):
    """Takes the graph in the current TensorFlow (Keras backend) session and saves it to a protobuf file at the provided path

    Saving consists of freezing the graph (converting all variables to constants), marking the outputs (using `output_names`)
    and writing the graph as binary to `output_model_path`

    Args:
        output_names: str
            the names of the output tensors to mark as outputs in the frozen graph
        output_model_path: str
            where to save the model (in binary protobuf format)

    Returns:
        The tf.GraphDef() of the graph after freezing
    """
    # Set the backend to 'test' mode (instead of 'train' mode)
    K.set_learning_phase(0)

    sess = K.get_session()
    # Freeze the graph (variables -> constants) and mark the outputs
    constant_graph_def = graph_util.convert_variables_to_constants(sess, sess.graph.as_graph_def(), output_names)
    # Write the frozen graph to a file
    graph_io.write_graph(constant_graph_def, os.path.dirname(output_model_path), os.path.basename(output_model_path), as_text=False)

    return constant_graph_def

def convert_and_save_model(model, output_model_file):
    """Converts a Keras model to a frozen TensorFlow graph and saves it in protobuf format to `output_model_file`

    Args:
        model: keras.models.Model
            the model to convert
        output_model_file: str
