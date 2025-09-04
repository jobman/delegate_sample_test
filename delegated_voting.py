import collections

class Voter:
    """
    Представляет одного избирателя в системе со взвешенным голосом (ставкой).
    """
    def __init__(self, name, stake=0.0):
        self.name = name
        self.stake = float(stake)  # Личная ставка (деньги)
        self.commitments = collections.defaultdict(float)  # Прямые голоса {'yes': amount, 'no': amount}
        self.delegates = []  # Список имен, кому делегирован остаток ставки

    def add_delegate(self, delegate_name):
        """Добавляет доверенное лицо."""
        self.delegates.append(delegate_name)

    def vote(self, choice, amount):
        """
        Фиксирует голос с определенным весом (количеством ставки).
        """
        if choice not in ['yes', 'no']:
            raise ValueError("Голос может быть только 'yes' или 'no'.")
        
        amount = float(amount)
        if amount < 0:
            raise ValueError("Количество не может быть отрицательным.")

        # Проверяем, не превышает ли общая сумма голосов личную ставку
        current_committed = sum(self.commitments.values()) - self.commitments[choice]
        if current_committed + amount > self.stake:
            raise ValueError(f"Недостаточно личной ставки. Доступно: {self.stake - current_committed:.2f}")
            
        self.commitments[choice] = amount

    def get_committed_stake(self):
        """Возвращает общую сумму ставки, использованной в прямых голосах."""
        return sum(self.commitments.values())

    def get_uncommitted_stake(self):
        """Возвращает долю личной ставки, которая не была использована и будет делегирована."""
        return self.stake - self.get_committed_stake()

    def __repr__(self):
        return f"Voter({self.name}, stake={self.stake}, commitments={self.commitments}, delegates={self.delegates})"

class VotingSystem:
    """
    Управляет процессом голосования и подсчетом результатов на основе ставок.
    Использует итеративный подход для разрешения делегирования.
    """
    def __init__(self):
        self.voters = {}

    def add_voter(self, name, stake=0.0):
        """Добавляет нового избирателя в систему."""
        if name not in self.voters:
            self.voters[name] = Voter(name, stake)
        return self.voters[name]

    def _calculate_voter_power(self, voter, power_dist):
        # 1. Начинаем с прямых голосов самого избирателя
        current_power = voter.commitments.copy()
        
        # 2. Добавляем мощность от делегирования (если есть неиспользованная ставка)
        uncommitted_stake = voter.get_uncommitted_stake()
        if voter.delegates and uncommitted_stake > 0:
            
            # Собираем суммарную мощность от всех делегатов из предыдущей итерации
            delegated_power = collections.defaultdict(float)
            for delegate_name in voter.delegates:
                if delegate_name in self.voters:
                    delegated_power['yes'] += power_dist[delegate_name]['yes']
                    delegated_power['no'] += power_dist[delegate_name]['no']
            
            total_delegated_power = sum(delegated_power.values())
            
            # Если у делегатов есть какая-то мощность, распределяем неиспользованную ставку
            if total_delegated_power > 0:
                yes_ratio = delegated_power['yes'] / total_delegated_power
                no_ratio = delegated_power['no'] / total_delegated_power
                
                current_power['yes'] += uncommitted_stake * yes_ratio
                current_power['no'] += uncommitted_stake * no_ratio

        return current_power

    def calculate_results(self, max_iterations=100, tolerance=1e-6):
        """
        Вычисляет и возвращает итоговые результаты голосования.
        
        Итеративно распространяет ставки по графу делегирования до стабилизации.
        """
        num_voters = len(self.voters)
        if num_voters == 0:
            return collections.defaultdict(float)

        power_dist = collections.defaultdict(lambda: collections.defaultdict(float))

        for i in range(max_iterations):
            next_power_dist = collections.defaultdict(lambda: collections.defaultdict(float))
            for name, voter in self.voters.items():
                next_power_dist[name] = self._calculate_voter_power(voter, power_dist)
            
            # Проверка на стабилизацию
            total_change = 0
            for name in self.voters:
                total_change += abs(next_power_dist[name]['yes'] - power_dist[name]['yes'])
                total_change += abs(next_power_dist[name]['no'] - power_dist[name]['no'])

            if total_change < tolerance:
                break
            
            power_dist = next_power_dist

        # 3. Подсчет итоговых результатов.
        final_tally = collections.defaultdict(float)
        for name in self.voters:
            final_tally['yes'] += power_dist[name]['yes']
            final_tally['no'] += power_dist[name]['no']
            
        return final_tally
