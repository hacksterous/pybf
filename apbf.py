#########################################################
# mpcap
# Minimalistic Python port of Complex ArbitraryPrecision
# Targeted for MicroPython on microcontrollers
# with a few tweaks 
# (c) 2020 Anirban Banerjee <anirbax@gmail.com>
#########################################################
global MPAP_DEGREES_MODE
global MPAPERRORFLAG
global APBF_PRECISION #31 bit APBF_PRECISION gives 23 accurate significant digits

MPAP_DEGREES_MODE = False
MPAPERRORFLAG = ''
APBF_PRECISION = 27

PYBF_CONST_PI = 0
PYBF_OP_MUL = 1
PYBF_OP_ADD = 2
PYBF_OP_SUB = 3
PYBF_OP_RINT = 4
PYBF_OP_ROUND = 5
PYBF_OP_CMP_EQ = 6
PYBF_OP_CMP_LT = 7
PYBF_OP_CMP_LE = 8
PYBF_OP_DIV = 9
PYBF_OP_FMOD = 10
PYBF_OP_REM = 11
PYBF_OP_SQRT = 12
PYBF_OP_OR = 13
PYBF_OP_XOR = 14
PYBF_OP_AND = 15
PYBF_OP_EXP = 16
PYBF_OP_LOG = 17
PYBF_OP_COS = 18
PYBF_OP_SIN = 19
PYBF_OP_TAN = 20
PYBF_OP_ATAN = 21
PYBF_OP_ATAN2 = 22
PYBF_OP_ASIN = 23
PYBF_OP_ACOS = 24
PYBF_OP_POW = 25

def degrees(val):
	global MPAP_DEGREES_MODE
	MPAP_DEGREES_MODE = bool(val)

def rprec():
	global APBF_PRECISION
	APBF_PRECISION = 27

def sprec(prec):
	global APBF_PRECISION
	APBF_PRECISION = prec
	print ("sprec: set APBF_PRECISION to ", APBF_PRECISION)

def gprec():
	return APBF_PRECISION

import pybf
pybf.initialize()

def pybfend():
	pybf.cleanup()
		
class mpap ():
	# Internal Representation of significant digits + sign.
	Mantissa = None

	# Internal Representation of (Integer) Exponent of 10,
	# e.g. 6.283012 = [Mantissa = 6283012, Exponent = 6]
	#	  0.097215 = [Mantissa = 97215  , Exponent = -2]
	# This exponent IS the scientific notation exponent.
	# Contrary to intuition, Mantissa * 10eExponent is NOT this number it
	# To reconstruct this number, take the first number and insert "." divider in 0-1 pos
	# e.g. 9.7215e-2, this is the actual number.
	# This is implied in later calculations, beware!
	Exponent = 0

	#True is positive, False is negative
	Sign = 1

	# __init__
	# Initialization Function
	# If a non-integer float type is passed to Mantissa, then this number will be converted
	# to our internal representation.
	#
	# (!!) IF YOU PASS A INTEGER TO mantissa there are two possible behaviors.
	# Your int may be interpreted
	# as a literal integer (InternalAware = False) or interpreted as internal representation of significant
	# digits, so 142857 = 1.42857x10^0 = 1.42857.
	# By default, we assume you are NOT aware of the Internal structures. This keeps consistency with float support
	# for mantissa.

	# Set InternalAware = True to interpret as internal representation.

	def processArguments (self, Mantissa, Exponent, InternalAware = False):
		global MPAPERRORFLAG
		try:
			#catch inf in Mantissa and illegal format in Exponent
			if type(Mantissa) == float:
				if str(float(Mantissa)) == 'inf' or str(float(Mantissa)) == '-inf' or \
					str(float(Mantissa)) == 'nan' or str(float(Exponent)) == 'nan' or \
					str(float(Exponent)) == 'inf' or str(float(Exponent)) == '-inf':
					raise OverflowError
			Exponent = int(Exponent)
		except (ValueError, OverflowError):
			selfMantissa = 0
			selfExponent = 0
			MPAPERRORFLAG = "Illegal mantissa or exponent. \nHint: use strings to hold large numbers!"
			raise ValueError

		if (type(Mantissa) == float or type(Mantissa) == str):
			# String rep of mantissa, useful for reuse (strings are immutable), also UnSigned variant
			strMan = str(Mantissa)
			strManUS = strMan.replace('-', '')
			# Extract all significant digits
			if('e' in strMan): # Oops, too small; have to expand notation
				# Something like 1e-07... significant digits are before e, then 
				# extract the second part and add it to exponent accumulator
				strManParts = strMan.split('e')
				try:
					selfMantissa = int(strManParts[0].replace('.', ''))
					Exponent += int(strManParts[1])
				except (ValueError, OverflowError):
					selfMantissa = 0
					selfExponent = 0
					MPAPERRORFLAG = "Illegal mantissa or exponent."
					raise ValueError
			else:
				try:
					selfMantissa = int(strMan.replace('.', ''))
				except (ValueError, OverflowError):
					selfMantissa = 0
					selfExponent = 0
					MPAPERRORFLAG = "Illegal mantissa or exponent."
					raise ValueError

			# Count exponent for scientific notation
			isFraction = (strManUS.find('.') > -1 and int(strManUS[:strManUS.find('.')]) == 0)
			#if (abs(float(Mantissa)) < 1) or isFraction == True:
			#print ("mpcap:processArguments - isFraction == ", isFraction)
			if isFraction == True:
				# numbers that cause single/double-precision float() to overflow
				# will fail this if-clause
				if selfMantissa == 0:
					#number is 0, .0, 0.0, 0. etc
					selfMantissa = 0
					selfExponent = 0
					Exponent = 0
				else:
					#number is a fraction
					for i in range(len(strManUS)):
						if(strManUS[i] == '.'):
							continue
						if(strManUS[i] != '0'):
							break
						Exponent = Exponent - 1
			else:
				Exponent = Exponent - 1 # 1.42857 is 1.425847e0
				for i in range(len(strManUS)):
					if(strManUS[i] == 'e' or  strManUS[i] == '.'):
						break
					Exponent = Exponent + 1

			selfExponent = Exponent

		else:
			#handle integer parameters only
			if(Mantissa == 0):
				selfMantissa = 0
				selfExponent = 0
			else:
				selfMantissa = Mantissa
				if InternalAware == True:
					selfExponent = Exponent
				else:
					selfExponent = Exponent + len(str(Mantissa).replace('-', '')) - 1
			
		#endif

		#M=10, E=1 and M=1, E=1 both indicate the same number,
		#however, the different values of mantissa will be a problem
		#in numeric comparisons, so reduce to the form M=1, E=1
		MantissaStr = str(selfMantissa)
		#if selfMantissa > 1000:
			#print ("mpcap: processArguments - MantissaStr is > 1000 and = ", MantissaStr)
		i = 0
		while MantissaStr[-1:] == '0' and \
				selfMantissa != 0:
			MantissaStr = MantissaStr[:-1]
			i += 1
		selfMantissa = int (MantissaStr)

		#print ("--------------- mpcap: processArguments - now returning")
		return selfMantissa, selfExponent

	def __init__(self, Mantissa, Exponent = 0,\
		IM = 0,\
		IE = 0, InternalAware = False
		):

		global APBF_PRECISION
		self.Precision = APBF_PRECISION
		if(isinstance(Mantissa, mpap)):
			self.Mantissa = Mantissa.Mantissa
			self.Exponent = Mantissa.Exponent
			self.IM = Mantissa.IM
			self.IE = Mantissa.IE
			return

		if Mantissa == 'inf' or Mantissa == '-inf' or Mantissa == 'nan' or Mantissa == 'err':
			self.Mantissa = Mantissa
			self.Exponent = Exponent
			return

		if IM == 'inf' or IM == '-inf' or IM == 'nan' or IM == 'err':
			self.IM = IM
			self.IE = IE
			return

		self.Mantissa, self.Exponent = self.processArguments (Mantissa, Exponent, InternalAware)
		self.IM, self.IE = self.processArguments (IM, IE, InternalAware)

		return
	#enddef init

	def bfwrapper (self, op, other=0):
		#print ("bfwrapper: calling bf_op with precision = ", APBF_PRECISION)
		s = pybf.bf_op(APBF_PRECISION, op, self.scistr(), mpap(other).scistr())
		s = s.split('s')[0]
		return mpap(s)

	def __truediv__ (self, other):
		global MPAPERRORFLAG
		#print ("---------------------------------")
		#print ("__truediv__: self = ", self)
		#print ("__truediv__: other = ", other)
		if(not isinstance(other, mpap)):
			return self / mpap(other)

		if self.IM != 0 or other.IM != 0:
			return self.ctruediv(other)

		if other == 0:
			MPAPERRORFLAG = "Division by zero."
			return mpap(0)

		PREC = max(self.Precision, other.Precision)
		PREC = max(self.Exponent, PREC)
		#print ("truediv: start: PREC = ", PREC)

		#subtract divisor's exponent from dividend's exponent after adjusting
		#for the InternalAware representaiton
		re = self.Exponent - (len(str(self.Mantissa).replace('-', '')) - 1)
		re -= other.Exponent - (len(str(other.Mantissa).replace('-', '')) - 1)

		#do division of the mantissa integers with the set precision
		rm = mpap(self.Mantissa).bfwrapper(PYBF_OP_DIV, mpap(other.Mantissa))
		#then adjust the exponent calculated earlier
		rm = mpap(Mantissa = str(rm), Exponent = re, InternalAware = True)
		return rm

	def isComplex(self):
		return self.IM != 0

	def isInt(self):
		# 123456 --> (123456, 5)
		return len(str(self.Mantissa).replace('-', '')) <= self.Exponent + 1

	def isIntIm(self):
		#imaginary part is integer
		return len(str(self.IM).replace('-', '')) <= self.IE + 1

	def isNaNInf (self):
		return self.Mantissa == None and self.Exponent == 0

	def isNone (self):
		return self.Mantissa == None or self.Exponent == None

	def int(self, preserveType = True):
		#print ("mpcap:int: Received ", self.__repr__())
		s = str(self.Mantissa)
		if s[0] == '-':
			mNeg = '-'
			s = s[1:]
		else:
			mNeg = ''
		#print ("mpcap:int: mantissa is ", str(self.Mantissa))
		if self.Exponent < 0:
			s = '0'
		else:
			lenS =len(s)
			#fill up with requisite number of 0s on the right
			#if more than 1e8, can run out of memory
			s = s + '0'*(self.Exponent + 1 - lenS)
			#take as many required by the Exponent (add 1 more
			#since canonical form is always #.##....e###
			s = s[0:(self.Exponent + 1)]

		if preserveType == True:
			#convert to an integer, but return the mpap() version
			return mpap(mNeg+s)
		else:
			return int(mNeg+s)

	def __int__ (self):
		#print ("mpcap:__int__: Received ", self.__repr__())
		return self.int(preserveType = False)

	def __float__ (self):
		#only for CPython, does not work in MicroPython
		return self.float()

	def float (self):
		s = str(self.Mantissa)
		return float(('-' if self.sgn() == -1 else '') + s[0:1] + '.' + s[1:] + 'e' + str(self.Exponent))

	def __repr__(self):
		return "mpap(Mantissa = " + str(self.Mantissa) + ", Exponent = " + str(self.Exponent) +\
				", IM = " + str(self.IM) + ", IE = " + str(self.IE) +\
				", InternalAware = True)"

	def cstr(self, sci=True):
		imL = '[' if self.IM != 0 else ''
		imR = ']' if self.IM != 0 else ''

		r = (mpap (Mantissa = self.Mantissa, Exponent = self.Exponent, InternalAware = True)).flexstr(sci)
		j = (mpap (Mantissa = self.IM, Exponent = self.IE, InternalAware = True)).flexstr(sci)

		if self.Mantissa == 0 or self.Exponent < -self.Precision:
			r = ''
			if self.IM < 0:
				j = '-[' + j[1:] + ']'
			else:
				j = '[' + j + ']'
		elif self.IM < 0:
			j = ' - [' + j[1:] + ']'
		else:
			j = ' + [' + j + ']'

		return r + j

	def __str__(self):
		return self.flexstr(sci=True)

	def flexstr(self, sci=True):
		#sci = True indicates that fractional values 
		#(those with abs smaller than 1)
		if self.IM != 0:
			return self.cstr(sci)
		#print ("mpcap:__str__: Received ", self.__repr__())

		if self.isInt():
			return str(int(self))
		elif len(str(self.Mantissa)) - 1 > self.Exponent and self.Exponent >= 0:
			#do not return as 1.23e45
			strAbsSelfMantissa = str(abs(self.Mantissa))
			decPoint = self.Exponent + 1
			return ('-' if self.Mantissa < 0 else '') + strAbsSelfMantissa[:decPoint] + '.' + strAbsSelfMantissa[decPoint:]
		else:
			strAbsSelfMantissa = str(abs(self.Mantissa))
			if sci == True:
				frac = strAbsSelfMantissa[1:]
				# mpap(1, -3) is 1.0e-3 and not 1.e-3
				if frac == '':
					frac = '0'
				strAbsSelfMantissa = strAbsSelfMantissa[0] + '.' + frac
				return ('-' if self.Mantissa < 0 else '') + strAbsSelfMantissa + "e" + str(self.Exponent)
			else:
				strAbsSelfMantissa = '0.' + '0'*(abs(self.Exponent) - 1) + strAbsSelfMantissa
				return ('-' if self.Mantissa < 0 else '') + strAbsSelfMantissa

	# return number in the form of
	# Mantissa = ###.#######, Exponent = ###*3
	# returns new mantissa as a string with a decimal point
	# and the exponent as an integer
	def sci(self):
		#print ("self is ", repr(self))
		man = str(self.Mantissa)
		expo = self.Exponent
		#print ("man is ", man)
		#print ("expo is ", expo)
		strMantissa = str(man).replace('-', '')
		lenStrMantissa = len(strMantissa)
		if self.Exponent <= 0:
			# we increase the exponent value to the nearest negative
			# upper multiple and compensate by adding more 0s to the
			#mantissa string
			if self.Exponent % 3 != 0:
				multfac = (3-abs(self.Exponent)%3)
				#print ("1. multfac is ", multfac)
				expo = self.Exponent - multfac
				if  lenStrMantissa < multfac + 1:
					strMantissa +=  '0'*(multfac+1-lenStrMantissa)
			else:
				multfac = 0
			man = ('-' if (self.sgn() == -1) else '') + strMantissa[:multfac+1] + '.' + strMantissa[multfac+1:]

		else:
			diff = self.Exponent - lenStrMantissa + 1 
			if diff < 0:
				diff += 3 # 3 additional places
			strMantissa = strMantissa + '0'*diff
			expo = self.Exponent
			multfac = self.Exponent % 3 + 1
			#print ("2. multfac is ", multfac)
			expo = (expo// 3) * 3
			man = ('-' if (self.sgn() == -1) else '') + strMantissa[:multfac] + '.' + strMantissa[multfac:]
		# handle the case when mantissa string is like '123.' -- add a zero at end

		if man.find ('.') != -1:
			man = man.rstrip('0')
			if man[-1:] == '.':
				man += '0'
		elif man.find('.') == -1:
			man += '.0'
		
		return man, expo

	# similar to sci(), but returns a single string as ###.#######e###
	def scistr(self):
		m, e = self.sci()
		return m + 'e' + str(e)

	def floor(self):
		i = self.int(preserveType = True)
		return i if self.sgn() >= 0 else i-1

	def __neg__(self):
		return mpap(Mantissa = (-1) * self.Mantissa, Exponent = self.Exponent, 
				IM = (-1) * self.IM, IE = self.IE,
				InternalAware = True)

	def __floordiv__ (self, other):
		if(not isinstance(other, mpap)):
			return self // mpap(other)
		#for negative numbers, round downwards, not towards 0
		res = (self / other).floor()
		return res

	def fpart (self, x):
		y = x - (x).floor()
		if y < 0:
			y += 1
		return y

	def nround (self, n):
		#round up for +
		#round down for -
		#n is a power of 10
		if self == 0:
			return mpap(0)
		if self > 0:
			return (self*n + 0.5).int()/n
		else:
			return (self*n - 0.5).int()/n

	def modexp (self, other, mod):
		#modular exp
		if not isinstance(other, mpap) or not isinstance(mod, mpap):
			return self.modexp(mpap(other), mpap(mod))
		if mod == 1:
			return mpap(0)
		base = int(self)
		exponent = int(other)
		modulus = int(mod)
		result = 1
		base = base % modulus
		while exponent > 0:
			if (exponent & 0b1 == 1):
				result = (result * base) % modulus
			exponent = exponent >> 1
			base = (base * base) % modulus
		return mpap(result)

	def modinv2 (self, other):
		s = 0
		olds = 1
		r = int (other)
		oldr = int(self)

		while r != 0:
			q = oldr // r

			newr = oldr - q*r
			oldr = r
			r = newr

			news = olds - q*s
			olds = s
			s = news

		if oldr > 1:
			#not invertible
			return mpap(0)
		else:
			if olds < 0:
				olds += other
			return mpap(olds)

	def modinv(self, other):
		x, y = self.extgcd(other)
		if x < 0:
			x += other
		return x

	def extgcd (self, other):
		s = 0
		olds = 1
		t = 1
		oldt = 0
		r = int (other)
		oldr = int(self)

		while r != 0:
			q = oldr // r

			newr = oldr - q*r
			oldr = r
			r = newr

			news = olds - q*s
			olds = s
			s = news

			newt = oldt - q*t
			oldt = t
			t = newt

		return mpap(olds), mpap(oldt)

	def __mod__ (self, other):
		if(not isinstance(other, mpap)):
			return self % mpap(other)

		s = self.bfwrapper(PYBF_OP_FMOD, other)
		#modulo result has same sign as divisor
		if other.sgn() == 1:
			if s < 0:
				s += other 
		elif other.sgn() == -1:
			if s > 0:
				s += other 
		return s

	def abs (self):
		return self.__abs__()

	def __abs__(self):
		if self.IM != 0:
			r = mpap (Mantissa = self.Mantissa, Exponent = self.Exponent, InternalAware = True)
			j = mpap (Mantissa = self.IM, Exponent = self.IE, InternalAware = True)
			return (r*r+j*j).sqrt()
			
		if(self.sgn() == 1):
			return self
		else:
			return -self

	def __eq__(self, other):
		if(not isinstance(other, mpap)):
			return self == mpap(other)
		internal = self - other

		#TODO: simplify this logic
		if internal.Exponent < -self.Precision:
			#equal
			if internal.IM != 0:
				if internal.IE < -self.Precision:
					#print ("__eq__internal is ", internal.__repr__(), " and returning True")
					return True
				elif internal.IM == 0:
					return True
				else:
					return False
			else:
				return True
		elif internal.Mantissa == 0:
			#print ("__eq__internal is ", internal.__repr__(), " and returning True")
			if internal.IM != 0:
				if internal.IE < -self.Precision:
					#print ("__eq__internal is ", internal.__repr__(), " and returning True")
					return True
				elif internal.IM == 0:
					return True
				else:
					return False
			else:
				return True
		else:
			#print ("__eq__internal is ", internal.__repr__(), " and returning False")
			return False

	def __hash__(self):
		return hash((self.Mantissa, self.Exponent))

	def re (self):
		return mpap(Mantissa = self.Mantissa, Exponent = self.Exponent, InternalAware = True)

	def im (self, imval = None):
		if imval is None:
			r = mpap(Mantissa = self.IM, Exponent = self.IE, InternalAware = True)
			#print ("function im: r = ", r.__repr__(), "sign = ", r.sgn())
			return r
		else:
			imval = mpap(imval)
			self.IM = imval.Mantissa
			self.IE = imval.Exponent
			return self

	def __ne__(self, other):
		return not self == other

	def __lt__(self, other):
		if(not isinstance(other, mpap)):
			return self < mpap(other)

		if self.IM != 0 or other.IM != 0:
			internal = abs(self) - abs(other)
			if internal.Exponent < -self.Precision:
				#equal
				return False
			elif internal.Mantissa < 0:
				return True
			else:
				return False

		internal = self - other
		if internal.Exponent < -self.Precision:
			#equal
			return False
		elif internal.Mantissa < 0:
			return True
		else:
			return False

	def __le__(self, other):
		return self == other or self < other

	def __gt__(self, other):
		return not self < other and not self == other

	def __ge__(self, other):
		return self == other or self > other

	def conj (self):
		#complex conjugate (r, i) -> (r, -i)
		if self.IM == 0:
			return self
		
		return mpap (Mantissa = self.Mantissa, 
						Exponent = self.Exponent, 
						IM = -self.IM,
						IE = self.IE,
						InternalAware = True)

	def ctruediv (self, other):
		#complex add
		if(not isinstance(other, mpap)):
			return self.ctruediv(mpap(other))
	
		r = mpap (Mantissa = other.Mantissa, Exponent = other.Exponent, InternalAware = True)
		j = mpap (Mantissa = other.IM, Exponent = other.IE, InternalAware = True)
		r = mpap(1)/(r*r + j*j)
		r = (self * other.conj()) * r
		return r

	def cadd(self, other):
		#complex add
		if(not isinstance(other, mpap)):
			return self.cadd(mpap(other))
	
		r = mpap (Mantissa = self.Mantissa, Exponent = self.Exponent, InternalAware = True) +\
			mpap (Mantissa = other.Mantissa, Exponent = other.Exponent, InternalAware = True)

		j = mpap (Mantissa = self.IM, Exponent = self.IE, InternalAware = True) +\
			mpap (Mantissa = other.IM, Exponent = other.IE, InternalAware = True)

		return mpap (Mantissa = r.Mantissa, 
						Exponent = r.Exponent, 
						IM = j.Mantissa,
						IE = j.Exponent,
						InternalAware = True)

	def cmul (self, other):
		#complex add
		if(not isinstance(other, mpap)):
			return self.cmul(mpap(other))
	
		r = (mpap (Mantissa = self.Mantissa, Exponent = self.Exponent, InternalAware = True) *\
			mpap (Mantissa = other.Mantissa, Exponent = other.Exponent, InternalAware = True)) -\
			(mpap (Mantissa = self.IM, Exponent = self.IE, InternalAware = True) *\
			mpap (Mantissa = other.IM, Exponent = other.IE, InternalAware = True))

		j = (mpap (Mantissa = self.Mantissa, Exponent = self.Exponent, InternalAware = True) *\
			mpap (Mantissa = other.IM, Exponent = other.IE, InternalAware = True)) +\
			(mpap (Mantissa = other.Mantissa, Exponent = other.Exponent, InternalAware = True) *\
			mpap (Mantissa = self.IM, Exponent = self.IE, InternalAware = True))

		return mpap (Mantissa = r.Mantissa, 
						Exponent = r.Exponent, 
						IM = j.Mantissa,
						IE = j.Exponent,
						InternalAware = True)

	def __add__(self, other):
		if (not isinstance(other, mpap)):
			return self + mpap(other)

		if self.IM != 0 or other.IM != 0:
			return self.cadd(other)

		return self.bfwrapper(PYBF_OP_ADD, other)

	def csub (self, other):
		if(not isinstance(other, mpap)):
			return self.csub(mpap(other))

		r = mpap (Mantissa = self.Mantissa, Exponent = self.Exponent, InternalAware = True) -\
			mpap (Mantissa = other.Mantissa, Exponent = other.Exponent, InternalAware = True)

		j = mpap (Mantissa = self.IM, Exponent = self.IE, InternalAware = True) -\
			mpap (Mantissa = other.IM, Exponent = other.IE, InternalAware = True)

		return mpap (Mantissa = r.Mantissa, 
						Exponent = r.Exponent, 
						IM = j.Mantissa,
						IE = j.Exponent,
						InternalAware = True)

	def __sub__(self, other):
		if(not isinstance(other, mpap)):
			return self - mpap(other)

		if self.IM != 0 or other.IM != 0:
			return self.csub(other)

		return self.bfwrapper(PYBF_OP_SUB, other)

	def __mul__(self, other):
		# To perform arithmetic multiplication, the exponents are multiplied together
		# and the mantissa are aligned and multiplied together.
		# This means we need to align all problems like this:
		# 1.42951e-5 (142951, -5) x 8.37e4 (837, 4) = 142951 x e(-5-5) x 837 x e(4-2)
		if(not isinstance(other, mpap)):
			return self * mpap(other)

		if self.IM != 0 or other.IM != 0:
			return self.cmul(other)

		PREC = max(self.Precision, other.Precision)
		PREC = max(self.Exponent, PREC)
		return self.bfwrapper(PYBF_OP_MUL, other)

	def __lshift__ (self, other):
		if(not isinstance(other, mpap)):
			return self << mpap(other)
		return self * mpap(2) ** other

	def __rshift__ (self, other):
		if(not isinstance(other, mpap)):
			return self >> mpap(other)
		return self / mpap(2) ** other

	def __xor__ (self, other):
		if(not isinstance(other, mpap)):
			return self != mpap(other)
		return mpap(int(self) ^ int(other))

	def __or__ (self, other):
		if(not isinstance(other, mpap)):
			return self | mpap(other)
		return mpap(int(self) | int(other))

	def __and__ (self, other):
		if(not isinstance(other, mpap)):
			return self & mpap(other)
		return mpap(int(self) & int(other))

	def __invert__ (self):
		return mpap(~int(self))

	def __not__ (self):
		return True if self == 0 else False

	def __pow__(self, other):
		global MPAPERRORFLAG
		if(not isinstance(other, mpap)):
			return self ** mpap(other)
		
		if self.IM != 0 or other.IM != 0:
			return self.pow(other)
		else:
			if(other == 0):
				return mpap(1)
			else:
				return self.bfwrapper(PYBF_OP_POW, other)

	def sgn(self):
		#should we round here?
		#if abs(x) < mpap(1, -prec) return 0?
		if self.Mantissa < 0:
			return -1
		elif self.Mantissa > 0:
			return 1
		else:
			return 0

	def pow (self, other):
		if(not isinstance(other, mpap)):
			return self ** mpap(other)
		#complex power 

		# ans = (r + i*j) ** (p + i*q)
		# log(ans) = (p + i*q) * log(r + i*j)
		# ans = exp ((p + i*q) * log(r + i*j))
		#print ("called generic pow function using exp and log...")
		return (other * self.log()).exp()

	def clog (self):
		global MPAP_DEGREES_MODE
		isDeg = MPAP_DEGREES_MODE
		degrees (False) #set to radians

		im = self.im()
		re = self.re()

		if re != 0:
			if re > 0:
				r = re.log()
				j = mpap(0)
			else:
				#log of a negative number = log (-1) * log of the negative of the negative number
				#log (-1) = pi * i
				r = (-re).log()
				j = mpap(mpap(1).pi())

			imdre = (im/re)
			r += (imdre*imdre + 1).log()/2
			j += imdre.atan()
		else:
			r = im.log() #if im == 0, log will set MPAPERRORFLAG
			j = mpap(0.5).pi() * im.sgn()
		pi = mpap(1).pi()
		if j > pi:
			j -= pi * 2
		degrees (isDeg) #restore old value
		return mpap (Mantissa = r.Mantissa, 
					Exponent = r.Exponent, 
					IM = j.Mantissa,
					IE = j.Exponent,
					InternalAware = True)

	def log (self):
		print ("mpcap.log: self =", self)
		if  self.IM != 0 or self.re () < 0:
			return self.clog()
		else:
			return self.bfwrapper(PYBF_OP_LOG)

	def pi(self):
		return self.bfwrapper(PYBF_CONST_PI)

	def pi_DONTUSE(self):
		# Pi using Chudnovsky's algorithm
		K, M, L, X, S = mpap(6), mpap(1), mpap(13591409), mpap(1), mpap(13591409)
		#NOTE: only for precision <= 27!!!
		maxK = min(self.Precision//5, 50)
		for i in range(1, maxK+1):
			M = (K**3 - K*16) * M // i**3 
			L += 545140134
			X *= -262537412640768000
			S += M * L / X
			K += 12
		Z = mpap(10005).sqrt()
		pi = Z * 426880 / S
		return pi * self

	def x10p (self, x):
		# multiply by 10^x, where x is an integer
		return mpap(self.Mantissa, self.Exponent+int(x), InternalAware=True)

	def isqrt (self):
		return self.isqrtnaive()

	def isqrtnaive(self):
		#Naive implementation O(n*n)
		#https://cs.stackexchange.com/questions/37596/arbitrary-precision-integer-square-root-algorithm
		x = int(self)
		r = 0
		i = x.bit_length()
		while i >= 0:
			inc = (r << (i+1)) + (1 << (i*2))
			if inc <= x:
				x -= inc
				r += 1 << i
			i -= 1
		return mpap(r)

	def sqrt (self):
		if  self.IM != 0:
			return (self.log()/2).exp()

		if self.re () < 0:
			r = (-self.re()).sqrt()
			return mpap(Mantissa=0, Exponent=0, IM=r.Mantissa, IE=r.Exponent, InternalAware = True)

		return self.bfwrapper(PYBF_OP_SQRT)

	def digits(self):
		return mpap(len(str(int(self))))

	def cexp (self):
		global MPAP_DEGREES_MODE
		isDeg = MPAP_DEGREES_MODE
		degrees (False) #set to radians

		r = mpap (Mantissa = self.Mantissa, Exponent = self.Exponent, InternalAware = True)
		j = mpap (Mantissa = self.IM, Exponent = self.IE, InternalAware = True)

		rexp = r.exp()
		r = rexp * j.cos()
		j = rexp * j.sin()

		degrees (isDeg) #restore old value
		return mpap (Mantissa = r.Mantissa, 
						Exponent = r.Exponent, 
						IM = j.Mantissa,
						IE = j.Exponent,
						InternalAware = True)

	def exp (self):
		if self.IM != 0:
			return self.cexp()
		else:
			return self.bfwrapper(PYBF_OP_EXP)

	def cosh (self):
		return (self.exp() + (-self).exp())/2

	def sinh (self):
		return (self.exp() - (-self).exp())/2

	def tanh (self):
		return self.sinh()/self.cosh()

	def tan (self):
		global MPAPERRORFLAG

		if self.IM != 0:
			return self.ctan()

		if self == mpap(0.5).pi():
			MPAPERRORFLAG = "Tangent is undefined."
			return mpap(0)

		if MPAP_DEGREES_MODE == True:
			d2r = mpap(1).pi() / 180
			return (self * d2r).bfwrapper(PYBF_OP_TAN)
		else:
			return self.bfwrapper(PYBF_OP_TAN)

	def atan2 (self, other):
		global MPAPERRORFLAG
		global MPAP_DEGREES_MODE

		if other == 0:
			MPAPERRORFLAG = "Tangent is undefined."
			return mpap(0)

		val = self.bfwrapper(PYBF_OP_ATAN2, other)

		if MPAP_DEGREES_MODE == True:
			d2r = mpap(1).pi() / 180
			return val * d2r
		else:
			return val

	def ctan (self):
		return self.csin()/self.ccos()

	def ccos (self):
		global MPAP_DEGREES_MODE
		isDeg = MPAP_DEGREES_MODE
		degrees (False) #set to radians

		#cos (r + i j) = cos(r) cosh(j) - i sin(r) sinh(j)
		r = mpap (Mantissa = self.Mantissa, Exponent = self.Exponent, InternalAware = True)
		j = mpap (Mantissa = self.IM, Exponent = self.IE, InternalAware = True)

		rr = r.cos() * j.cosh()
		jr = r.sin() * j.sinh()

		degrees (isDeg) #restore old value
		return mpap (Mantissa = rr.Mantissa, 
						Exponent = rr.Exponent, 
						IM = -jr.Mantissa,
						IE = jr.Exponent,
						InternalAware = True)

	def csin (self):
		global MPAP_DEGREES_MODE
		isDeg = MPAP_DEGREES_MODE
		degrees (False) #set to radians

		#sin (r + i j) = sin(r) cosh(j) + i cos(r) sinh(j)
		r = mpap (Mantissa = self.Mantissa, Exponent = self.Exponent, InternalAware = True)
		j = mpap (Mantissa = self.IM, Exponent = self.IE, InternalAware = True)

		rr = r.sin() * j.cosh()
		jr = r.cos() * j.sinh()

		degrees (isDeg) #restore old value
		return mpap (Mantissa = rr.Mantissa, 
						Exponent = rr.Exponent, 
						IM = jr.Mantissa,
						IE = jr.Exponent,
						InternalAware = True)

	def sin (self):
		global MPAP_DEGREES_MODE
		if self.IM != 0:
			return self.csin()

		if self == 0:
			return mpap(0)

		if MPAP_DEGREES_MODE == True:
			x = self * mpap(1).pi() / mpap(180)
		else:
			x = self

		return x.bfwrapper(PYBF_OP_SIN)

	def cos (self):
		global MPAP_DEGREES_MODE
		if self.IM != 0:
			return self.ccos()

		if MPAP_DEGREES_MODE == True:
			x = self * mpap(1).pi() / mpap(180)
		else:
			x = self

		return x.bfwrapper(PYBF_OP_COS)

	def acos (self):
		if self.IM != 0:
			return mpap(0.5).pi() - self.casin()
		return self.asin(acosine=True)

	def casin (self):
		i = mpap(Mantissa = 0, 
					Exponent = 0, IM = 1, IE = 0, InternalAware = True)
			
		return (-i) * (i * self + (mpap(1) - self*self).sqrt()).log()

	def asin (self, acosine=False):
		print ("NEW ASIN")
		global MPAP_DEGREES_MODE
		global MPAPERRORFLAG
		if abs(self) > 1:
			MPAPERRORFLAG = "Domain error."
			return mpap(0)

		if abs (self - 1) < mpap(1, -self.Precision):
			if acosine == False:
				v = mpap(0.5).pi()
			else:
				return mpap(0)
		else:
			return self.bfwrapper(PYBF_OP_ASIN)
			

		if MPAP_DEGREES_MODE == True:
			#r2d = mpap(180) / mpap('3.1415926535897932384626433832795')
			r2d = mpap(180) / mpap(1).pi()
			#return (mpap(1).pi()/2 - v)*r2d  if acosine==True else v*r2d
			return (mpap(0.5).pi() - v)*r2d  if acosine==True else v*r2d
		else:
			#return mpap(1).pi()/2 - v if acosine==True else v
			return mpap(0.5).pi() - v if acosine==True else v

	def catan(self):
		i = mpap(Mantissa = 0, 
					Exponent = 0, IM = 1, IE = 0, InternalAware = True)
		if self != i:
			#catan is not defined for i
			return ((i + self)/(i - self)).log() * (i/2)
		else:
			return mpap(0)

	def atan (self):
		global MPAP_DEGREES_MODE
		if self.IM != 0:
			return self.catan()

		ret = self.bfwrapper(PYBF_OP_ATAN)
		
		if MPAP_DEGREES_MODE == True:
			r2d = mpap(180) / mpap(1).pi()
			return ret * r2d
		else:
			return ret

	def endian(self, boundary=8):
		boundary = int(boundary)
		if boundary == 0:
			boundary = 8;
		copy = self
		result = mpap(0)
		while copy != 0:
			result <<= boundary
			result |= (copy & ((1<<boundary)-1))
			copy >>= boundary

		return result
	
	def factors (self):
		n = int(self)

		if n == 0:
			self.result = 0
	
		self.result = set()
		self.result |= {int(1), n}
	
		def all_multiples(result, n, factor):
			z = n
			f = int(factor)
			while z % f == 0:
				result |= {f, z // f}
				f += factor
			return result
		
		self.result = all_multiples(self.result, n, 2)
		self.result = all_multiples(self.result, n, 3)
		
		for i in range(1, int(self.isqrt()) + 1, 6):
			i1 = i + 1
			i2 = i + 5
			if not n % i1:
				self.result |= {int(i1), n // i1}
			if not n % i2:
				self.result |= {int(i2), n // i2}

		print (self.result)
		return mpap(1)

