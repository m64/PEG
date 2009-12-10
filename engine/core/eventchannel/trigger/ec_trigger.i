/***************************************************************************
 *   Copyright (C) 2005-2008 by the FIFE team                              *
 *   http://www.fifengine.de                                               *
 *   This file is part of FIFE.                                            *
 *                                                                         *
 *   FIFE is free software; you can redistribute it and/or                 *
 *   modify it under the terms of the GNU Lesser General Public            *
 *   License as published by the Free Software Foundation; either          *
 *   version 2.1 of the License, or (at your option) any later version.    *
 *                                                                         *
 *   This library is distributed in the hope that it will be useful,       *
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU     *
 *   Lesser General Public License for more details.                       *
 *                                                                         *
 *   You should have received a copy of the GNU Lesser General Public      *
 *   License along with this library; if not, write to the                 *
 *   Free Software Foundation, Inc.,                                       *
 *   51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA          *
 ***************************************************************************/

%module fife
%{
#include "eventchannel/trigger/ec_trigger.h"
%}

%include "ec_trigger.i"
%include "ec_itriggercontroller.i"
%include "ec_itriggerlistener.i"

namespace FIFE {

        class Trigger : public ITriggerController {

        public:
                Trigger(ITriggerListener& listener);

                void registerTrigger(Trigger& trigger);

                void unregisterTrigger(Trigger& trigger);

                void registerListener(ITriggerListener& triggerlistener);

                void unregisterListener(ITriggerListener& triggerlistener);
        };
}