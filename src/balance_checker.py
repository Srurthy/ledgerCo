#!/usr/bin/env python3
import math

from src.logger import logger


class Loan():
    # Initialize the class variables with the input from the loan
    def __init__(self,
                 bankname,
                 person,
                 principal_amount,
                 tenure,
                 rate):
        self.bankname = bankname
        self.person = person
        self.principal_amount = principal_amount
        self.tenure = tenure
        self.rate = rate
        self.lump_sum = []

    def get_emi(self):
        repay_amount = self.get_total_repayable_amount()
        try:
            # Get the monthly emi from total amount to pay
            return math.trunc(math.ceil(float(repay_amount)/(self.tenure*12)))
        except:
            logger.warning("Error in emi calculation")

    def get_total_emi_nos(self):
        """
        Method to find the count of emi's within the loan tenure
        """
        try:
            return math.trunc(math.ceil(self.tenure*12))
        except:
            logger.warning("Error in total emi calculation")

    def get_total_repayable_amount(self):
        """
        I = P*N*R
        """
        return (self.principal_amount
                + (self.principal_amount
                   * self.tenure
                   * self.rate)/100)

    def get_lumpsum_amount_paid(self, emi_number):
        """
        Method to find out the total lumpsum amount until given emi
        """
        try:
            lumpsum_paid_before_cur_emi = filter(
                lambda item: item["emi_number"] <= emi_number,
                self.lump_sum)
            if lumpsum_paid_before_cur_emi:
                total_lump_sum_amount = sum(
                    [item["amount"] for item in lumpsum_paid_before_cur_emi]
                )
                return total_lump_sum_amount
            else:
                return 0
        except:
            logger.warning("Error in finding total mumpsum amount")

    def get_last_emi(self, amount_paid):
        """
        After deducting the lumpsum, if the final amount to be paid is less 
        than the emi. The emi amount would be adjusted to that amount
        """
        last_emi = self.get_total_repayable_amount() - amount_paid
        emi_amount = self.get_emi()
        if emi_amount > last_emi:
            return last_emi
        else:
            return emi_amount

    def payment(self, lump_sum_amount, emi_number):
        """
        Method add the lmpsum payment
        """
        self.lump_sum.append({
            "emi_number": emi_number,
            "amount": lump_sum_amount
        })

    def balance(self, emi_number):
        """
        Method to find out the balance
        """
        # If the emi_number entered is higher than the tenure period all 
        # the amount would be paid by that time and no remaining emis
        if emi_number >= self.get_total_emi_nos():
            pending_emi_nos = 0
            amount_paid = self.get_total_repayable_amount()
        else:
            try:
                emi_amount = self.get_emi()
                if self.lump_sum:
                    # Get the amount paid until the current emi
                    amount_paid = (emi_number-1) * emi_amount
                    # Add the lumpsum amount untill that
                    amount_paid += self.get_lumpsum_amount_paid(
                        emi_number
                    )
                    # Find the last emi amount. If it is last emi there is 
                    # probability of changing the amount
                    amount_paid += self.get_last_emi(amount_paid)
                    payable_amount = float(
                        self.get_total_repayable_amount() - amount_paid
                    )
                    # Calculate the emi number from the remaining amount to 
                    # pay
                    if payable_amount:
                        pending_emi_nos = math.trunc(
                            math.ceil(payable_amount/emi_amount))
                    else:
                        pending_emi_nos = 0
                        amount_paid = self.get_total_repayable_amount()
                else:
                    amount_paid = (emi_number) * emi_amount
                    pending_emi_nos = self.get_total_emi_nos() - emi_number
            except:
                logger.warning("Error in balance calculation")
        return {
            "bankname": self.bankname,
            "person": self.person,
            "amount_paid": amount_paid,
            "pending_emi_nos": pending_emi_nos
        }
