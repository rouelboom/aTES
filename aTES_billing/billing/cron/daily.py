"""
Daily handlers
"""
from datetime import datetime

from aiohttp.web_request import Request

from billing import const
from billing.dao.dao_billing import DAOBilling
from billing.dao.dao_users import DAOUsers
from billing.rmq.callbacks import stream_new_operation
from billing.rmq.message_publishing import get_message, publish_message
from billing.rmq.publisher import RabbitMQPublisher
from billing.schema_registry.validator import SchemaRegistryValidator


# Сори, походу тут будет весь код в одном файле

def get_start_date():
    current_datetime = datetime.now()
    midnight = current_datetime.replace(hour=0, minute=0)
    return midnight


def get_end_date():
    current_datetime = datetime.now()
    end_of_day = current_datetime.replace(hour=23, minute=59, second=59)
    return end_of_day


async def withdraw_money(user_id: str, money_amount: int):
    """Placeholder for API to withdraw money system"""
    return True


async def publish_withdraw_money_event(
        withdraw_data: dict,
        routing_key: str,
        publisher: RabbitMQPublisher,
        validator: SchemaRegistryValidator
):
    message = get_message(withdraw_data, const.EVENT__WITHDRAW_1, validator)
    await publish_message(
        publisher,
        routing_key,
        message
    )


async def handle_daily_withdraw(request: Request):
    """
    Process daily withdraw for workers which have positive balance
    """
    app = request.app

    # список того, что надо сделать:
    # закрыть billing cycle и открыть новый (чтобы все новые операции записывались уже в новый бц)
    # получить всех работников
    # посчитать его (каждого работника) доход за billing cycle
    # совершить выплату (отправить запрос в сторонний апи, типа)
    # если запрос успешный (что делать если не успешный в рамках дз рассматривать не будем):
    # выполнить транзакцию на списание (использовать billing_cycle_id который мы уже закрыли,
    # хз на сколько это корректно, я бы сказал что допустимо. хотя можно было бы заблокировать операции
    # на время расчёта (прям как "у нас обед"), однако в рамках дз мне кажется это ту мач)
    # кинуть сообщение о новой транзакции
    # обнулить баланс
    dao_billing = app['dao_billing']  # type: DAOBilling
    dao_users = app['dao_users']  # type: DAOUsers
    operation_publisher = app['operation_publisher']
    billing_event_publisher = app['billing_event_publisher']
    schema_validator = app['schema_validator']

    billing_cycle = await dao_billing.get_current_billing_cycle()
    billing_cycle_id = billing_cycle[const.ID]
    await dao_billing.close_billing_cycle(billing_cycle_id)

    await dao_billing.create_new_billing_cycle(get_start_date(), get_end_date())
    workers = await dao_users.get_all_workers()

    for worker in workers:
        worker_id = worker[const.ID]
        balance = await dao_billing.get_personal_balance(worker_id)
        if balance <= 0:
            return
        await withdraw_money(worker_id, balance)
        withdraw_data = {
            'receiver_id': worker_id,
            'amount_of_money': balance,
            'withdraw_time': datetime.now().isoformat(),
            'description': 'Income for period since {start_date} to {end_date}'.format(
                start_date=billing_cycle[const.START_DATE], end_date=billing_cycle[const.END_DATE]
            )
        }
        await publish_withdraw_money_event(
            withdraw_data,
            app['config']['exchanges']['billing']['name'],
            billing_event_publisher,
            schema_validator
        )
        operation = {
            const.BILLING_CYCLE_ID: billing_cycle_id,
            const.TIME: datetime.now().isoformat(),
            const.DESCRIPTION: 'salary',
            const.WORKER_ID: worker_id,
            const.CREDIT: 0,
            const.DEBIT: balance
        }
        operation[const.ID] = await dao_billing.add_operation(operation)
        await stream_new_operation(
            operation,
            app['config']['exchanges']['operation_streaming']['name'],
            operation_publisher,
            schema_validator
        )
