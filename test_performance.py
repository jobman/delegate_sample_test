
import pytest
import time
import random
import os
from delegated_voting import VotingSystem

def generate_random_voting_system(num_voters):
    """Создает систему голосования со случайными связями."""
    system = VotingSystem()
    voter_names = [f"Voter_{i}" for i in range(num_voters)]

    for name in voter_names:
        system.add_voter(name, stake=random.uniform(10, 1000))

    for name in voter_names:
        voter = system.voters[name]
        
        # С некоторой вероятностью избиратель голосует напрямую
        if random.random() < 0.7:
            vote_amount = random.uniform(0, voter.stake)
            choice = random.choice(['yes', 'no'])
            try:
                voter.vote(choice, vote_amount)
            except ValueError:
                # Игнорируем ошибку, если случайно сгенерировали слишком большой голос
                pass

        # С некоторой вероятностью избиратель делегирует свой голос
        if random.random() < 0.8:
            num_delegates = random.randint(1, min(5, num_voters - 1))
            delegates = random.sample([n for n in voter_names if n != name], num_delegates)
            for delegate_name in delegates:
                voter.add_delegate(delegate_name)
                
    return system

@pytest.mark.parametrize("num_voters", [10, 100, 1000, 10000, 100000, 1000000])
def test_algorithm_performance(num_voters):
    """
    Тестирует производительность алгоритма, выводит результат в консоль
    и сохраняет его в файл 'performance_results.csv'.
    """
    print(f"\n--- Тест производительности для {num_voters} избирателей ---")
    
    # 1. Генерация системы
    generation_start_time = time.monotonic()
    system = generate_random_voting_system(num_voters)
    generation_end_time = time.monotonic()
    print(f"Время на генерацию данных: {generation_end_time - generation_start_time:.4f}s")

    # 2. Запуск и измерение времени выполнения алгоритма
    start_time = time.monotonic()
    results = system.calculate_results()
    end_time = time.monotonic()
    
    elapsed_time = end_time - start_time
    
    # 3. Вывод результатов
    print(f"Итоговые голоса: Yes={results.get('yes', 0):.2f}, No={results.get('no', 0):.2f}")
    print(f"Время выполнения алгоритма: {elapsed_time:.4f}s")

    # 4. Сохранение результатов в файл
    results_file = "performance_results.csv"
    # Создаем заголовок, если файл не существует
    if not os.path.exists(results_file):
        with open(results_file, 'w', encoding='utf-8') as f:
            f.write("num_voters,elapsed_time_s\n")
    
    # Добавляем новую запись
    with open(results_file, 'a', encoding='utf-8') as f:
        f.write(f"{num_voters},{elapsed_time:.4f}\n")

    # 5. Проверка, что время выполнения не превышает 1 минуту
    assert elapsed_time < 60, f"Время выполнения ({elapsed_time:.2f}s) превысило лимит в 60 секунд."

    print("-" * 40)
