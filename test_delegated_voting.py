import pytest
from delegated_voting import Voter, VotingSystem
import collections

def test_delegated_voting_scenarios():
    system = VotingSystem()

    # Создаем избирателей с их ставками (деньгами)
    system.add_voter("Alice", stake=100)
    system.add_voter("Bob", stake=50)
    system.add_voter("Charlie", stake=20)
    system.add_voter("David", stake=100)
    system.add_voter("Eve", stake=30)
    system.add_voter("Frank", stake=10) # Делегирует в цикл
    system.add_voter("George", stake=10) # Член цикла
    system.add_voter("Harry", stake=10) # Член цикла

    # 1. Прямое голосование полной ставкой
    system.voters["Alice"].vote("yes", 100)
    
    # 2. Прямое голосование частью ставки
    system.voters["Bob"].vote("no", 30)

    # 3. Простое делегирование
    system.voters["Charlie"].add_delegate("Alice")

    # 4. Делегирование нескольким участникам
    system.voters["David"].add_delegate("Alice")
    system.voters["David"].add_delegate("Bob")

    # 5. Смешанное голосование: часть ставки напрямую, остаток делегируется
    system.voters["Eve"].vote("yes", 10)
    system.voters["Eve"].add_delegate("Bob")

    # 6. Делегирование в изолированный цикл
    system.voters["George"].add_delegate("Harry")
    system.voters["Harry"].add_delegate("George")
    system.voters["Frank"].add_delegate("George")

    # Пересчитываем голоса на основе делегирования
    final_tally = system.calculate_results()

    # Ожидаемый вклад каждой ставки:
    # Alice: 100 yes (напрямую)
    # Bob: 30 no (напрямую)
    # Charlie (-> Alice): 20 yes
    # David (-> Alice, Bob): 76.92 yes, 23.08 no (приблизительно)
    # Eve (10 'yes' напрямую, 20 -> Bob): 10 yes, 20 no
    # Frank, George, Harry: 30 потеряно в цикле
    # ИТОГО ОЖИДАЕТСЯ: 100 + 20 + 76.92 + 10 = 206.92 yes, 30 + 23.08 + 20 = 73.08 no
    # ПОТЕРЯНО: 20 (Bob) + 30 (цикл) = 50

    # Проверяем итоговые результаты
    assert final_tally['yes'] == pytest.approx(206.92, abs=1e-2)
    assert final_tally['no'] == pytest.approx(73.08, abs=1e-2)

    total_votes_cast = final_tally['yes'] + final_tally['no']
    total_stake = sum(v.stake for v in system.voters.values())
    lost_stake = total_stake - total_votes_cast

    assert total_stake == 330.0
    assert total_votes_cast == pytest.approx(280.0, abs=1e-2)
    assert lost_stake == pytest.approx(50.0, abs=1e-2)