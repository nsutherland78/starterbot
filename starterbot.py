import os
import time
import subnetcalc
from slackclient import SlackClient
from argparse import ArgumentParser


# starterbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">:"
sncalc = subnetcalc

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))


def create_parser():
    parser = ArgumentParser(
        description='Calculates subnets'
    )
    parser.add_argument(
        '-n',
        '--network',
        type=str,
        help='Enter an IP network in NN.NN.NN.NN/SS, NN.NN.NN.NN/SS.SS.SS.SS or NN.NN.NN.NN/WW.WW.WW.WW notation'
    )
    parser.add_argument(
        '-p',
        '--prefix',
        type=int,
        help='This value specifies the provided networks prefix length to display in the subnetworks output'
    )
    return parser.parse_args()


def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    ARGS = create_parser()
    response = "Not sure what you mean. Use the *" + "subnetcalc" + \
               "* command with numbers, delimited by spaces."
    if command.startswith("subnetcalc"):
        response = subnetcalc.main(ARGS)
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                    output['channel']
    return None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1  # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
