import logging

import click

from .common import common_options, pass_state, SharedArgs

from ..indexer import IndexerQueueHandler
from ..scheduler import NetkanScheduler
from ..spacedock_adder import SpaceDockAdder
from ..mirrorer import Mirrorer


@click.command()
@common_options
@pass_state
def indexer(common: SharedArgs) -> None:
    IndexerQueueHandler(common).run()


@click.command()
@click.option(
    '--max-queued', default=20, envvar='MAX_QUEUED',
    help='SQS Queue to send netkan metadata for scheduling',
)
@click.option(
    '--group',
    type=click.Choice(['all', 'webhooks', 'nonhooks']), default="nonhooks",
    help='Which mods to schedule',
)
@click.option(
    '--game', help='Which Game to Schedule for Inflation',
)
@click.option(
    '--min-cpu', default=200,
    help='Only schedule if we have at least this many CPU credits remaining',
)
@click.option(
    '--min-io', default=70,
    help='Only schedule if we have at least this many IO credits remaining',
)
@common_options
@pass_state
def scheduler(
    common: SharedArgs,
    max_queued: int,
    group: str,
    game: str,
    min_cpu: int,
    min_io: int
) -> None:
    sched = NetkanScheduler(
        common, common.queue, common.token, game,
        nonhooks_group=(group in ('all', 'nonhooks')),
        webhooks_group=(group in ('all', 'webhooks')),
    )
    if sched.can_schedule(max_queued, common.dev, min_cpu, min_io):
        sched.schedule_all_netkans()
        logging.info("NetKANs submitted to %s", common.queue)


@click.command()
@common_options
@pass_state
def mirrorer(common: SharedArgs) -> None:
    # We need at least 50 mods for a collection for ksp2, keeping
    # to just ksp for now
    Mirrorer(
        common.game('ksp').ckanmeta_repo, common.ia_access, common.ia_secret,
        common.game('ksp').ia_collection, common.token
    ).process_queue(common.queue, common.timeout)


@click.command()
@common_options
@pass_state
def spacedock_adder(common: SharedArgs) -> None:
    sd_adder = SpaceDockAdder(
        common.queue,
        common.timeout,
        common.netkan_repo,
        common.github_pr,
    )
    sd_adder.run()
