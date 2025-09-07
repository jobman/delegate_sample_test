from collections import defaultdict

class Person:
    def __init__(self, name, balance=1.0):
        self.name = name
        self.balance = balance
        self.delegates = []
        self.is_voter = False

    def add_delegate(self, delegate):
        self.delegates.append(delegate)

    def __repr__(self):
        return f"Person({self.name}, balance={self.balance}, delegates={[d.name for d in self.delegates]}, is_voter={self.is_voter})"

class VotingSystem:
    def __init__(self):
        self.people = {}

    def get_person(self, name, balance=1.0):
        if name not in self.people:
            self.people[name] = Person(name, balance)
        elif balance != 1.0:
            self.people[name].balance = balance
        return self.people[name]

    def setup_delegations(self, delegations, balances):
        for name, balance in balances.items():
            self.get_person(name, balance)

        for delegator_name, delegate_names in delegations.items():
            delegator = self.get_person(delegator_name)
            for delegate_name in delegate_names:
                delegate = self.get_person(delegate_name)
                delegator.add_delegate(delegate)

    def set_voters(self, voted_names):
        for person in self.people.values():
            person.is_voter = False
        for name in voted_names:
            if name in self.people:
                self.people[name].is_voter = True

    def distribute_votes(self):
        final_votes = defaultdict(float)
        for person in self.people.values():
            if person.is_voter:
                final_votes[person.name] = person.balance

        votes_to_distribute = {
            person: person.balance
            for person in self.people.values()
            if not person.is_voter
        }

        num_rounds = len(self.people) * 2

        for _ in range(num_rounds):
            if not votes_to_distribute:
                break
            
            next_round_votes = defaultdict(float)
            
            for person, weight in votes_to_distribute.items():
                if not person.delegates:
                    continue

                share = weight / len(person.delegates)
                for delegate in person.delegates:
                    if delegate.is_voter:
                        final_votes[delegate.name] += share
                    else:
                        next_round_votes[delegate] += share
            
            votes_to_distribute = next_round_votes

        return dict(final_votes)
