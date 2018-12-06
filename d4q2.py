#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 19 15:42:02 2018

@author: arnaud
"""

###############################################################################
# Apprentissage et reconnaissance
# GIF-4101 / GIF-7005, Automne 2018
# Devoir 4, Question 2
#
###############################################################################
############################## INSTRUCTIONS ###################################
###############################################################################
#
# - RepÃ©rez les commentaires commenÃ§ant par TODO : ils indiquent une tÃ¢che que
#       vous devez effectuer.
# - Vous ne pouvez PAS changer la structure du code, importer d'autres
#       modules / sous-modules, ou ajouter d'autres fichiers Python
# - Ne touchez pas aux variables, TMAX*, ERRMAX* et _times, Ã  la fonction
#       checkTime, ni aux conditions vÃ©rifiant le bon fonctionnement de votre
#       code. Ces structures vous permettent de savoir rapidement si vous ne
#       respectez pas les requis minimum pour une question en particulier.
#       Toute sous-question n'atteignant pas ces minimums se verra attribuer
#       la note de zÃ©ro (0) pour la partie implÃ©mentation!
#
###############################################################################

import time
import random

import numpy as np

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.optim import SGD
from torch.utils.data import DataLoader

from torchvision.datasets import ImageFolder
from torchvision.models import resnet18
import torchvision.transforms as T

from d4utils import CODES_DE_SECTION
from d4utils import compute_accuracy

# TODO Logistique
# Mettre 'BACC' ou 'GRAD'
SECTION = 'BACC'

# TODO Logistique
# Mettre son numÃ©ro d'Ã©quipe ici
NUMERO_EQUIPE = 4

# CrÃ©e la random seed
RANDOM_SEED = CODES_DE_SECTION[SECTION] + NUMERO_EQUIPE


class LegoNet(nn.Module):

    def __init__(self, pretrained=False):
        super().__init__()

        # CrÃ©e le rÃ©seau de neurone prÃ©-entraÃ®nÃ©
        self.model = resnet18(pretrained=pretrained)

        # RÃ©cupÃ¨re le nombre de neurones avant
        # la couche de classification
        dim_before_fc = self.model.fc.in_features

        # TODO Q2A
        # Changer la derniÃ¨re fully-connected layer
        # pour avoir le bon nombre de neurones de
        # sortie
        self.model.fc = nn.Linear(dim_before_fc, 16)

        if pretrained:
          # TODO Q2A
          # Geler les paramÃ¨tres qui ne font pas partie
          # de la derniÃ¨re couche fc
          # Conseil: utiliser l'itÃ©rateur named_parameters()
          # et la variable requires_grad
          for name, param in self.model.named_parameters():
            if name != 'fc.weight' and name != 'fc.bias':
              param.requires_grad = False
          
    def forward(self, x):
        # TODO Q2B
        # Appeler la fonction forward du rÃ©seau
        # prÃ©-entraÃ®nÃ© (resnet18) de LegoNet
        y = self.model.forward(x)
        return y


if __name__ == '__main__':
    # DÃ©finit la seed
    torch.manual_seed(RANDOM_SEED)
    torch.cuda.manual_seed_all(RANDOM_SEED)

    # Des effets stochastiques peuvent survenir
    # avec cudnn, mÃªme si la seed est activÃ©e
    # voir le thread: https://bit.ly/2QDNxRE
    torch.backends.cudnn.deterministic = True

    # TODO Q2D
    # Faire rouler le code une fois sans prÃ©-entrainement
    # et l'autre fois avec prÃ©-entraÃ®nement
    pretrained = True

    # DÃ©finit si cuda est utilisÃ© ou non
    # mettre cuda pour utiliser un GPU
    device = 'cpu'

    # DÃ©finit les paramÃ¨tres d'entraÃ®nement
    # Nous vous conseillons ces paramÃ¨tres. Or, vous pouvez
    # les changer
    nb_epoch = 1
    learning_rate = 0.01
    momentum = 0.9
    batch_size = 64

    # DÃ©finit les transformations nÃ©cessaires pour
    # le chargement du dataset
    totensor = T.ToTensor()
    normalize = T.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])
    composition = T.Compose([totensor, normalize])

    # Charge le dataset d'entraÃ®nement
    train_set = ImageFolder(root ='data/lego/lego/train', transform=composition)

    # CrÃ©e un gÃ©nÃ©rateur alÃ©atoire avec la seed
    context_random = random.Random(RANDOM_SEED)

    # Selectionne 10% du jeu de test alÃ©atoirement pour allÃ©ger le calcul
    test_set = ImageFolder('data/lego/lego/test', transform=composition)
    idx = context_random.sample(range(len(test_set)), k=int(0.1 * len(test_set)))
    test_set.samples = [test_set.samples[i] for i in idx]

    # TODO Q2C
    # CrÃ©er les dataloader pytorch avec la
    # classe DataLoader de pytorch
    train_loader = DataLoader(train_set, batch_size=batch_size,
                                shuffle=True)
    test_loader = DataLoader(test_set, batch_size=batch_size,
                                shuffle=True)

    # TODO Q2C
    # Instancier un rÃ©seau LegoNet
    # dans une variable nommÃ©e "model"
    model = LegoNet(pretrained)
    
    #Si load est vrai on charge le modèle entrainé et sauvegardé dans
    #le repertoire courrant    
    load = True
    
    if (load):
        try:
            if(pretrained):
                model.load_state_dict(torch.load('lego_model_pretrained.pt'))
            else:
                model.load_state_dict(torch.load('lego_model_not_pretrained.pt'))
        except:
            #Cas ou il n'y a pas de classifieur enregistré
            load = False

    # Tranfert le rÃ©seau au bon endroit
    model.to(device)

    if not load:

        # TODO Q2C
        # Instancier une fonction d'erreur CrossEntropyLoss
        # et la mettre dans une variable nommÃ©e criterion
        criterion = nn.CrossEntropyLoss()

        # TODO Q2C
        # Instancier l'algorithme d'optimisation SGD
        # Conseil: Filtrer les paramÃ¨tres non-gelÃ©s!
        # Ne pas oublier de lui donner les hyperparamÃ¨tres
        # d'entraÃ®nement : learning rate et momentum!
        params = list(filter(lambda x: x.requires_grad, model.parameters()))
        optim = SGD(params = params, lr = learning_rate, momentum = momentum)

        # TODO Q2C
        # Mettre le rÃ©seau en mode entraÃ®nement
        model.train()

        # RÃ©cupÃ¨re le nombre total de batch pour une epoch
        total_batch = len(train_loader)

        # TODO Q2C
        # Remplir les TODO dans la boucle d'entraÃ®nement
        for i_epoch in range(nb_epoch):

            start_time, train_losses = time.time(), []
            for i_batch, batch in enumerate(train_loader):
                images, targets = batch

                images = images.to(device)
                targets = targets.to(device)

                # TODO Q2C
                # Mettre les gradients Ã  zÃ©ro
                optim.zero_grad()            

                # TODO Q2C
                # Calculer:
                # 1. l'infÃ©rence dans une variable "predictions"
                # 2. l'erreur dans une variable "loss"
                predictions = model.forward(images)
                loss = criterion(predictions, targets)

                # TODO Q2C
                # RÃ©tropropager l'erreur et effectuer
                # une Ã©tape d'optimisation
                loss.backward()
                optim.step()

                # Ajoute le loss de la batch
                train_losses.append(loss.item())

                print(' [-] batch {:4}/{:4} since {:.2f}s'.format(
                    i_batch+1, total_batch, time.time()-start_time))

            print(' [-] epoch {:4}/{:}, train loss {:.6f} in {:.2f}s'.format(
                i_epoch+1, nb_epoch, np.mean(train_losses), time.time()-start_time))

            # sauvegarde le rÃ©seau
            if pretrained:
                torch.save(model.state_dict(), 'lego_model_pretrained.pt')
            else:
                torch.save(model.state_dict(), 'lego_model_not_pretrained.pt')

    # affiche le score Ã  l'Ã©cran
    test_acc = compute_accuracy(model, test_loader, device)
    if pretrained:
        print(' [-] pretrained test acc. {:.6f}%'.format(test_acc * 100))
    else:
        print(' [-] not pretrained test acc. {:.6f}%'.format(test_acc * 100))