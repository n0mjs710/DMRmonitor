**Socket-Based Reporting for DMRlink**

Over the years, the biggest request recevied for DMRlinkn (other than call-routing/bridging tools) has been web-based diagnostics and/or statistics for the program.

I strongly disagree with including the amount of overhead this would require inside DMRlink -- which still runs nicely on very modest resources. That it does this, and is in Python is a point of pride for me... Just let me have this one, ok? What I have done is added some hooks to DMRlink, which will be expanded over time, whereby it listens on a TCP socket and provides the raw data necessary for a "web dashboard", or really any external logging or statisitcs gathering program.

DMRmonitor is my take on a "web dashboard" for DMRlink.

***THIS SOFTWARE IS VERY, VERY NEW***

Right now, I'm just getting into how this should work, what does work well, what does not... and I am NOT a web applications programmer, so yeah, that javascript stuff is gonna look bad. Know what you're doing? Help me!

It has now reached a point where folks who know what they're doing can probably make it work reasonably well, so I'm opening up the project to the public.

***GOALS OF THE PROJECT***

Some things I'm going to stick to pretty closely. Here they are:

+ DMRmonitor be one process that includes a webserver
+ Websockets are used for pushing data to the browser - no long-polling, etc.
+ Does not provide data that's easily misunderstood
+ Incorporates RCM with with repeaters to display their state

***0x49 DE N0MJS***

Copyright (C) 2013-2017  Cortney T. Buffington, N0MJS <n0mjs@me.com>

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
