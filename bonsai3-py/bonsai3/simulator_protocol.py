
"""
Protocol definitions for bonsai3 library
"""
__copyright__ = "Copyright 2020, Microsoft Corp."

# pyright: strict

from argparse import ArgumentParser
from datetime import datetime
from enum import Enum
import json
import os
import sys
from typing import Any, Dict, List, Optional

from .logger import Logger

log = Logger()

# CLI help strings
_ACCESS_KEY_HELP = \
    """
    The access key to use when connecting to the BRAIN server. If
    specified, it will be used instead of any access key
    information stored in a bonsai config file.
    """

_API_HOST_HELP = \
    """
    The api host is the host to which the simulator will connect.
    It has the form http[s]://<hostname>[:<port>]
    """

_WORKSPACE_HELP = \
    """
    This is the value of the workspace.
    """

_SIM_CONTEXT_HELP = \
    """
    This is an opaque string.
    """

_VERBOSE_HELP = "Enables logging. Alias for --log=all"

_LOG_HELP = \
    """
    Enable logging. Parameters are a list of log domains.
    Using --log=all will enable all domains.
    Using --log=none will disable logging.
    """

_RETRY_TIMEOUT_HELP = \
    """
    The time in seconds that reflects how long the simulator will attempt to
    reconnect to the backend. 0 represents do not reconnect. -1 represents
    retry forever. The default is set to 300 seconds (5 minutes).
    """

class ServiceConfig:
    """Configuration information needed to connect to the service."""
    server = ''  # type: str
    workspace = ''  # type: str
    access_key = ''  # type: str
    simulator_context = ''  # type: str

    retry_timeout_seconds = 300  # type: int
    network_timeout_seconds = 60  # type: int

    def __init__(self,
                 workspace: str='',
                 access_key: str='',
                 server: str='https://api.bons.ai',
                 argv: Optional[List[str]]=sys.argv):
        """
        Initialize a config object.
        
        Command line argument switches will take priority over environment variables.
        Environment variables will take priority over initializer parameters.
        """

        # defaults
        self.server = os.getenv('SIM_API_HOST', server)
        self.workspace = os.getenv('SIM_WORKSPACE', workspace)
        self.access_key = os.getenv('SIM_ACCESS_KEY', access_key)
        self.simulator_context = os.getenv('SIM_CONTEXT', '')
        self.retry_timeout_seconds = 300
        self.network_timeout_seconds = 60  # TODO: Maybe make network timeout configurable.

        # parse the args last
        if argv:
            self.argparse(argv)

    
    def argparse(self, argv: List[str]):
        ''' parser command line arguments '''
        parser = ArgumentParser(allow_abbrev=False)

        parser.add_argument('--accesskey', '--access-key', help=_ACCESS_KEY_HELP)
        parser.add_argument('--api-host', help=_API_HOST_HELP)
        parser.add_argument('--workspace', help=_WORKSPACE_HELP)
        parser.add_argument('--sim-context', help=_SIM_CONTEXT_HELP)
        parser.add_argument('--log', nargs='+', help=_LOG_HELP)
        parser.add_argument('--verbose', action='store_true',
                            help=_VERBOSE_HELP)
        parser.add_argument('--retry-timeout', type=int,
                            help=_RETRY_TIMEOUT_HELP)

        args, remainder = parser.parse_known_args(argv[1:])

        # quiet pyright
        if remainder:
            pass

        # unpack arguments
        if args.accesskey:
            self.access_key = args.accesskey

        if args.api_host:
            self.server = args.api_host

        if args.workspace:
            self.workspace = args.workspace

        if args.sim_context:
            self.simulator_context = args.sim_context

        if args.log is not None:
            for domain in args.log:
                log.set_enabled(domain)

        if args.verbose:
            self.verbose = args.verbose
            log.set_enable_all(args.verbose)

        if args.retry_timeout is not None:
            self.retry_timeout_seconds = args.retry_timeout

class SimulatorEventType(Enum):
    Registered = 'Registered'
    Idle = 'Idle'

    EpisodeStart = 'EpisodeStart'
    EpisodeStep = 'EpisodeStep'
    EpisodeFinish = 'EpisodeFinish'

    PlaybackStart = 'PlaybackStart'
    PlaybackStep = 'PlaybackStep'
    PlaybackFinish = 'PlaybackFinish'

    Unregister = 'Unregister'

Schema = Dict[str, Any]

class BaseEventData:
    def __init__(self, data: Schema):
        self.__dict__.update(data)

class EpisodeStartData(BaseEventData):
    config = {}  # type: Schema

class EpisodeStepData(BaseEventData):
    action = {}  # type: Schema

class EpisodeFinishData(BaseEventData):
    reason = ""  # type: str

class PlaybackStartData(BaseEventData):
    config = {}  # type: Schema

class PlaybackStepData(BaseEventData):
    action = {}  # type: Schema
    state = {}  # type: Schema
    terminal = False  # type: bool

class PlaybackFinishData(BaseEventData):
    pass

class IdleData(BaseEventData):
    callbackTime = 0 # type: int

class UnregisterData(BaseEventData):
    reason = ""  # type: str

class SimulatorEvent:
    """An Event received from the server."""

    def __init__(self, data: Schema):
        self.__dict__.update(data)

        if self.type:
            if self.type == SimulatorEventType.EpisodeStart.name and 'episodeStart' in data:
                self.episodeStart = EpisodeStartData(data['episodeStart'])
            if self.type == SimulatorEventType.EpisodeStep.name and 'episodeStep' in data:
                self.episodeStep = EpisodeStepData(data['episodeStep'])
            if self.type == SimulatorEventType.EpisodeFinish.name and 'episodeFinish' in data:
                self.episodeFinish = EpisodeFinishData(data['episodeFinish'])
            if self.type == SimulatorEventType.Idle.name and 'idle' in data:
                self.idle = IdleData(data['idle'])
            if self.type == SimulatorEventType.Unregister.name and 'unregister' in data:
                self.unregister = UnregisterData(data['unregister'])

    type = ""  # type: str
    sessionId = ""  # type: str
    sequenceId = 1  # type: int

    episodeStart = None    # type: Optional[EpisodeStartData]
    episodeStep = None     # type: Optional[EpisodeStepData]
    episodeFinish = None   # type: Optional[EpisodeFinishData]
    playbackStart = None   # type: Optional[PlaybackStartData]
    playbackStep = None    # type: Optional[PlaybackStepData]
    playbackFinish = None  # type: Optional[PlaybackFinishData]
    idle = None            # type: Optional[IdleData]
    unregister  = None     # type: Optional[UnregisterData]

    interface = None         # type: Optional[Dict]
    simulatorContext = None  # type: Optional[Dict]
    registrationTime = None  # type: Optional[datetime]
    lastSeenTime = None      # type: Optional[datetime]
    iterationRate = None     # type: Optional[int]
    details = None           # type: Optional[str]
    sessionStatus = None     # type: Optional[str]
    sessionProgress = None   # type: Optional[Dict]

class SimulatorInterface:
    """JSON Body sent to server describing the simulators capabilities."""
    def __init__(self,
        context: Optional[str] = None,
        json_file_path: Optional[str] = None,
        json_interface: Optional[str] = None):
        # prefer file path over raw string
        if json_file_path:
            try:
                log.info('Loading simulator interface file from: {}'.format(json_file_path))
                with open(json_file_path, 'r') as file:
                    json_interface = file.read()
            except:
                log.info('Failed to load interface file: {}'.format(json_file_path))
                raise

        # must have something
        if json_interface is None:
            json_interface = (
                '{' +
                '  "name": "",' +
                '  "timeout": 0' +
                '}'
            )

        self._interface = json.loads(json_interface)

        # Insert the opaque "context".
        if context:
            self._interface['simulatorContext'] = context or ''

    @property
    def name(self) -> Optional[str]:
        return self._interface['name']

    @name.setter
    def name(self, value: Optional[str]):
        self._interface['name'] = value

    @property
    def timeout(self) -> Optional[int]:
        return self._interface['timeout']

    @timeout.setter
    def timeout(self, value: Optional[int]):
        self._interface['timeout'] = value

    @property
    def json(self) -> str:
        return json.dumps(self._interface)

class SimulatorEventRequest:
    """JSON Body sent to server for next event requests."""
    sessionId = ""  # type: str
    sequenceId = 0  # type: int
    state = None    # type: Any
    halted = False  # type: bool
    error = None    # type: Optional[str]
