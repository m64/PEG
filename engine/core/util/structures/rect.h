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

/***************************************************************************

    Rectangle intersection code copied and modified from the guichan 0.4
    source, which is released under the BSD license.

    Copyright (c) 2004, 2005, 2006 Olof Naessén and Per Larsson All rights reserved.

    * Redistribution and use in source and binary forms, with or without modification,
      are permitted provided that the following conditions are met: 
      Redistributions of source code must retain the above copyright notice,
      this list of conditions and the following disclaimer.

    * Redistributions in binary form must reproduce the above copyright notice,
      this list of conditions and the following disclaimer in the documentation
      and/or other materials provided with the distribution.

    * Neither the name of the Guichan nor the names of its contributors may be used
      to endorse or promote products derived from this software without specific
      prior written permission.

 THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS
 OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
 AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
 CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
 OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
 GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
 AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
 OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

    For more Information about guichan see: http://guichan.sourceforge.net

****************************************************************************/

#ifndef FIFE_VIDEO_RECT_H
#define FIFE_VIDEO_RECT_H

// Standard C++ library includes
#include <iostream>

// 3rd party library includes

// FIFE includes
// These includes are split up in two parts, separated by one empty line
// First block: files included from the FIFE root src directory
// Second block: files included from the same folder
#include "point.h"

namespace FIFE {

	/** A Rectangle on screen.
	 *
	 * This is a small helper class used for screen coordinate arithmetics.
	 * The same thoughts reasong using @b int as value type as in Point apply.
	 *
	 * @see Point
	 */
	class Rect {
		public:
			/** The X Coordinate.
			 */
			int x;
			/** The Y Coordinate.
			 */
			int y;
			/** Width of the rectangle.
			 */
			int w;
			/** Height of the rectangle.
			 */
			int h;

			/** Constructor.
			 * 
			 * Creates a new Rect with the values defaulting to 0.
			 */
			explicit Rect(int x = 0, int y = 0, unsigned int width = 0, unsigned int height = 0);

			/** The X coordinate of the right edge.
			 */
			int right() const;

			/** The Y coordinate of the bottom edge.
			 */
			int bottom() const;

			/** Equivalence operator.
			 *
			 * @param rect The rectangle to which this is compared.
			 * @return True only if both rectangle values are all equal.
			 */
			bool operator==(const Rect& rect ) const;

			/** Checks whether a rectangle contains a Point.
			 *
			 * @param p The point that is checked.
			 * @return True if the point lies inside the rectangle or on one of its borders.
			 */
			bool contains( const Point& point ) const;

			/** Check whether two rectangles share some area.
			 *
			 * @param rect The other rectangle that is checked.
			 * @return True, if and only if both rectangles have some covered area in common.
			 * This includes edges that cover each other.
			 * @note This operation is commutative.
			 */
			bool intersects( const Rect& rect ) const;

			/** Calculate rectangle intersection in place
			 *
			 * @param rect The other rectangle that is checked.
			 * @return True, if and only if both rectangles have some covered area in common.
			 * This includes edges that cover each other.
			 */
			bool intersectInplace( const Rect& rect );

	};

	/** Stream output operator.
	 *
	 * Useful for debugging purposes, this will output the coordinates
	 * of the rectangle to the stream.
	 */
	std::ostream& operator<<(std::ostream&, const Rect&);


	//////////////// INLINE FUNCTIONS /////////////////////////

	inline 
	int Rect::right() const {
		return x + w;
	}

	inline 
	int Rect::bottom() const {
		return y + h;
	}


	inline 
	bool Rect::operator==(const Rect& rect ) const {
		return
			x == rect.x && y == rect.y && w == rect.w && h == rect.h;
	}


	inline
	bool Rect::contains( const Point& point ) const {
		return
			(((point.x >= x) && (point.x <= x + w))
				&& ((point.y >= y) && (point.y <= y + h)));
	}


	inline
	bool Rect::intersectInplace( const Rect& rectangle ) {
		x = x - rectangle.x;
		y = y - rectangle.y;

	
		if (x < 0) {
			w += x;
			x = 0;
		}
	
		if (y < 0) {
			h += y;
			y = 0;
		}
	
		if (x + w > rectangle.w) {
			w = rectangle.w - x;
		}
	
		if (y + h > rectangle.h) {
			h = rectangle.h - y;
		}
	
		x += rectangle.x;
		y += rectangle.y;

		if (w <= 0 || h <= 0) {
			h = 0;
			w = 0;
			return false;
		}
		return true;
	}


	inline
	bool Rect::intersects( const Rect& rectangle ) const {
		int _x = x - rectangle.x;
		int _y = y - rectangle.y;
		int _w = w;
		int _h = h;

	
		if (_x < 0) {
			_w += _x;
			_x = 0;
		}
	
		if (_y < 0) {
			_h += _y;
			_y = 0;
		}
	
		if (_x + _w > rectangle.w) {
			_w = rectangle.w - _x;
		}
	
		if (_y + _h > rectangle.h) {
			_h = rectangle.h - _y;
		}
	
		if (_w <= 0 || _h <= 0) {
			return false;
		}
		return true;
	}

}

#endif
