from models.apartment import ApartamentModel
import numpy as np
import pandas as pd

class ApartmentUtils():

    @classmethod
    def get_apartments(cls):
        apartments = ApartamentModel.get_all();
        pd_apartment = pd.DataFrame.from_records([apartment.to_dict() for apartment in apartments])
        pd_apartment.to_csv('filename.csv')
        ApartmentUtils.someCalculate(pd_apartment)
        return pd_apartment

    @classmethod
    def someCalculate(cls, data):
        X = data[:, 1]; y = data[:, 2];
        m = y.length

        X = [np.ones(m, 1), data[:, 1]];

        theta = np.zeros(2, 1);

        J = ApartmentUtils.computeCost(X, y, theta);

    @classmethod
    def computeCost(cls, X, y, theta):
        m = y.length
        J = 0;
        predictions = X * theta;
        sqrErrors = (predictions - y)** 2;
        J = 1 / (2 * m) * sum(sqrErrors);
        pass