import random

import numpy as np

import torch
import torch.nn.functional as F


def compute_saliency_maps(X, y, model):
    """
    Compute a class saliency map using the model for images X and labels y.

    Input:
    - X: Input images; Tensor of shape (N, 3, H, W)
    - y: Labels for X; LongTensor of shape (N,)
    - model: A pretrained CNN that will be used to compute the saliency map.

    Returns:
    - saliency: A Tensor of shape (N, H, W) giving the saliency maps for the input
    images.
    """
    # Make sure the model is in "test" mode
    model.eval()

    # Construct new tensor that requires gradient computation
    X = X.clone().detach().requires_grad_(True)
    saliency = None
    ##############################################################################
    # TODO: Implement this function. Perform a forward and backward pass through #
    # the model to compute the gradient of the correct class score with respect  #
    # to each input image. You first want to compute the loss over the correct   #
    # scores, and then compute the gradients with torch.autograd.gard.           #
    ##############################################################################
    a = model(X)
    loss_function = torch.nn.CrossEntropyLoss()
    loss = loss_function(a, y)    
    grad = torch.autograd.grad(loss, X)[0] # returns tuple of tensor
    N, H, W = len(X), len(X[0][0]), len(X[0][0][0])
    saliency = torch.zeros(N, H, W)

    for i in range(N):
        for j in range(H):
            for k in range(W):
                saliency[i, j, k] = max(abs(grad[i, 0, j, k]), abs(grad[i, 1, j, k]), abs(grad[i, 2, j, k]))
    saliency = saliency.detach()
    ##############################################################################
    #                             END OF YOUR CODE                               #
    ##############################################################################
    return saliency


def make_fooling_image(X, target_y, model):
    """
    Generate a fooling image that is close to X, but that the model classifies
    as target_y.

    Inputs:
    - X: Input image; Tensor of shape (1, 3, 224, 224)
    - target_y: An integer in the range [0, 1000)
    - model: A pretrained CNN

    Returns:
    - X_fooling: An image that is close to X, but that is classifed as target_y
    by the model.
    """
    # Initialize our fooling image to the input image.
    X_fooling = X.clone().detach().requires_grad_(True)

    learning_rate = 1
    ##############################################################################
    # TODO: Generate a fooling image X_fooling that the model will classify as   #
    # the class target_y. You should perform gradient ascent on the score of the #
    # target class, stopping when the model is fooled.                           #
    # When computing an update step, first normalize the gradient:               #
    #   dX = learning_rate * g / ||g||_2                                         #
    #                                                                            #
    # You should write a training loop.                                          #
    #                                                                            #
    # HINT: For most examples, you should be able to generate a fooling image    #
    # in fewer than 100 iterations of gradient ascent.                           #
    # You can print your progress over iterations to check your algorithm.       #
    ##############################################################################
    # blur_image(X, sigma=1)
    model.eval()
    for i in range(100):
        a = model(X_fooling)
        # loss_function = torch.nn.CrossEntropyLoss()
        loss = -a[0][target_y]
        grad = torch.autograd.grad(loss, X_fooling)[0] # returns tuple of tensor
        X_fooling = X_fooling - (learning_rate / torch.max(grad)) * grad # np.abs(grad).mean() another normalization # - because we want a different class than for our loss  
    ##############################################################################
    #                             END OF YOUR CODE                               #
    ##############################################################################
    return X_fooling.detach()


def update_class_visulization(model, target_y, l2_reg, learning_rate, img):
    """
    Perform one step of update on a image to maximize the score of target_y
    under a pretrained model.

    Inputs:
    - model: A pretrained CNN that will be used to generate the image
    - target_y: Integer in the range [0, 1000) giving the index of the class
    - l2_reg: Strength of L2 regularization on the image
    - learning_rate: How big of a step to take
    - img: the image tensor (1, C, H, W) to start from
    """

    # Create a copy of image tensor with gradient support
    img = img.clone().detach().requires_grad_(True)
    ########################################################################
    # TODO: Use the model to compute the gradient of the score for the     #
    # class target_y with respect to the pixels of the image, and make a   #
    # gradient step on the image using the learning rate. Don't forget the #
    # L2 regularization term!                                              #
    # Be very careful about the signs of elements in your code.            #
    ########################################################################
    # model.eval()
    a = model(img)
    loss = -(a[0][target_y] - l2_reg * torch.norm(img)**2)
    grad = torch.autograd.grad(loss, img)[0]
    img = img - (learning_rate ) * grad

    ########################################################################
    #                             END OF YOUR CODE                         #
    ########################################################################
    return img.detach()
