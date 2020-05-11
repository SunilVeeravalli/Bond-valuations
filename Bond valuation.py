import numpy as np
import pandas as pd
from datetime import datetime, date


class BondCalculations:
    """
    Summary
    ===========
    Computes future cash flows, value of the bond, current yield and approximated yield to maturity of a bond.

    Parameters
    ===========
    principal_amount: a float
        par value (or principal amount or the face value) of the bond
        Example: if the face value is $100, then principal_amount = 100
    coupon_rate: a float
        percentage of coupon rate. The amount of interest paid by the issuer.
        Example: if coupon rate is 5%, then coupon_rate = 0.05
    bond_issue_date: a string
        Bond issue date
        Example: If the bond was issued on 25th February 2000, then bond_issue_date = "2000-02-25"
    bond_maturity_date: a string
        Bond maturity (expiry) date
        Example: If the bond gets expired on 24th February 2020, then bond_maturity_date = "2020-02-24"
    discount_rate: a float
        The coupon rate is fixed for the bond when it gets issued. Discount rate is the current interest rate available in the market which could be inflation rate OR minimum expected rate of return from bonds of similar quality or credit rating.
        Example: If the yield is 4%, then discount_rate = 0.04
    coupon_payment_frequency: a string
        It is interest payment frequency and it takes any value: 'annually', 'semi_annually', 'quarterly', 'monthly' , 'weekly', 'daily'
        Example: coupon_payment_frequency = 'annually' (default)

    """
    def __init__(self,
                 principal_amount: np.float,
                 coupon_rate: np.float,
                 bond_issue_date: np.str,
                 bond_maturity_date: np.str,
                 discount_rate: np.float,
                 coupon_payment_frequency: np.str = 'annual'):
        self.principal_amount = principal_amount
        self.coupon_rate = coupon_rate
        self.bond_issue_date = datetime.strptime(bond_issue_date, '%Y-%m-%d').date()
        self.bond_maturity_date = datetime.strptime(bond_maturity_date, '%Y-%m-%d').date()
        self.discount_rate = discount_rate
        self.coupon_payment_frequency = coupon_payment_frequency
        # setting the current date (cd)
        self.cd = date.today() if date.today() >= self.bond_issue_date else self.bond_issue_date
        self.payments_per_year = {
            'annually'     : 1,
            'semi-annually': 2,
            'quarterly'    : 4,
            'monthly'      : 12,
            'weekly'       : 52,
            'daily'        : 365
        }

    def present_value(self, row: pd.Series) -> np.float:
        """
        This is used in the method "bond_value()" to calculate the present value from future date and amount.
        fd = future date
        fv = future value
        n = no. of years
        t = no. of times compounded in a year
        pv = present value
        """
        fd = row['receivable_date']
        fv = row['receivable_amount']
        n = (fd - self.cd).days / 365
        t = self.payments_per_year[self.coupon_payment_frequency]
        pv = fv / ((1 + (self.discount_rate / t)) ** (n * t))
        return pv

    def bond_value(self) -> (pd.DataFrame, np.float):
        """
        Summary
        ===========
        Computes future cash flows and the value of the bond (expected selling price).
        
        Returns
        ========
        A tuple with two elements:
            a dataframe: contains all the cash flows
            a float: value of the bond
        
        Calculation
        ===========
        The present value of a bond is: sum of present value (PV) of all future interest payments receivable and present value (PV) of future principal amount receivable.
        The calculation assumes that the coupon payment received is reinvested as they are received.
        """
        no_of_periods = (self.bond_maturity_date - self.bond_issue_date).days / (
                    365 / self.payments_per_year[self.coupon_payment_frequency])
    
        df = pd.DataFrame({
            'receivable_date'  : pd.date_range(start = self.bond_issue_date,
                                               end = self.bond_maturity_date,
                                               periods = no_of_periods + 1).date,
            'receivable_amount': (self.principal_amount * self.coupon_rate) / self.payments_per_year[self.coupon_payment_frequency]
        })
    
        # Keeping only those dates where the coupon payment will be received
        df = df[df['receivable_date'] > self.cd]
    
        # On the maturity date, along with final coupon payment, the principal amount will also be received.
        df.loc[df['receivable_date'] == self.bond_maturity_date, 'receivable_amount'] += self.principal_amount
    
        df['present_value'] = df.apply(func = self.present_value, axis = 1)
    
        return df, df['present_value'].sum()
    
    def yield_calculations(self, current_bond_price: np.float) -> (np.float, np.float):
        """
        Summary
        =======
        Computes current yield and approximated yield to maturity of the bond.
        Current yield
            return earned if held the bond for a year.
        Yield to maturity
            return earned if held the bond till maturity.
        
        Parameters
        ==========
        current_bond_price: a float
            The current market price of the bond.
        
        Returns
        =======
        A tuple with two elements:
            a float: current_yield
            a float: approximated yield to maturity
        
        Calculation
        ===========
                          r * F
        Current yield = ---------
                            P
        
                             F - P
                        C + -------
                               n
        Approx. YTM = ------------------
                             F + P
                            -------
                               2
        where:
            r = coupon rate
            F = principal amount
            P = current bond price
            C = interest received per year
            n = no of years left
        """
        current_yield = (self.coupon_rate * self.principal_amount) / current_bond_price

        receivable_per_year = self.principal_amount * self.coupon_rate
        no_of_year_left = (self.bond_maturity_date - self.cd).days / 365
        yield_to_maturity = (receivable_per_year + ((self.principal_amount - current_bond_price) / no_of_year_left)) / ((self.principal_amount + current_bond_price) / 2)
        return current_yield, yield_to_maturity
    
    
bc = BondCalculations(
    principal_amount = 500,
    coupon_rate = 0.1,
    bond_issue_date = '2030-01-01',
    bond_maturity_date = '2039-12-31',
    discount_rate = 0.12,
    coupon_payment_frequency = 'quarterly')
cash_flow, value_of_bond = bc.bond_value()
print(cash_flow)
print(value_of_bond)
cy, ytm = bc.yield_calculations(current_bond_price = 400)
print(cy)
print(ytm)














