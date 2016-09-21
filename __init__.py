from __future__ import print_function
from rtmidi import MidiIn, MidiOut
from rtmidi.midiutil import open_midiport
from Queue import Queue

# mapping between event type and constructor
event_type_to_mapping = {
    8: NoteOffMapping,
    9: NoteOnMapping,
    11: ControlChangeMapping,
}

def listener(msg_queue):
    while True:


def main():
    ports = MidiIn().get_ports()
    if not ports:
        print("No midi ports available.")
        return
    print("Available input ports:\n{}".format(ports))
    portnum = int(raw_input("Please select a port number: "))
    msg_queue = Queue()
    port, name = open_midiport(portnum)

    def handle_midi_event(event, data):
        (b0, b1, b2), _ = event
        event_type, channel = b0 >> 4, b0 & 7
        message = (event_type, channel, b2)
        msg_queue.put(("midi", message))
    port.set_callback(handle_midi_event)

message_type_to_event_type = {
    'NoteOff': 8 << 4,
    'NoteOn': 9 << 4,
    'ControlChange': 11 << 4,
}

def list_ports():
    """Print the available ports."""

    log.info("Available output ports:\n{}".format(MidiOut().get_ports()))



class MidiInput (object):
    """A queue-based system for dealing with receiving midi messages."""

    def __init__(self):
        """Initialize the message queue."""
        self.queue = Queue()
        self.ports = {}
        #self.mappings = defaultdict(set)
        self.controllers = set()

    def register_controller(self, controller):
        """Register a midi controller with the input service."""
        self.controllers.add(controller)

    def unregister_controller(self, controller):
        """Unregister a midi controller from the input service."""
        self.controllers.discard(controller)

    def open_port(self, port_number):
        """Open a new midi port to feed the message queue."""
        port, name = open_midiport(port_number)
        self.ports[name] = port

        queue = self.queue
        def parse(event, data):
            (b0, b1, b2), _ = event
            event_type, channel = b0 >> 4, b0 & 7
            message = (event_type_to_mapping[event_type](channel, b1), b2)
            queue.put(message)
        port.set_callback(parse)

    def close_port(self, port_name):
        port = self.ports.pop(port_name)
        port.cancel_callback()
        port.close_port()

    def receive(self, timeout=None):
        """Block until a message appears on the queue, then dispatch it.
        Optionally specify a timeout in seconds.
        """
        message = self.queue.get(timeout=timeout)
        log.debug("received {}".format(message))
        self._dispatch(*message)
        return message

    def _dispatch(self, mapping, payload):
        """Dispatch a midi message to the registered handlers."""
        for controller in self.controllers:
            handler = controller.controls.get(mapping, None)
            if handler is not None:
                handler(mapping, payload)