/* MOEPOLY - This R5 program is fixed heavily by Raybit Tang(PolyGameLab)
 * From 10/24/2012
 *
 */


#include "Config.h" 
#include "stdafx.h"

#include <stdlib.h>
#include <conio.h>
#include <iostream>

#include <string>
#include <fstream>

#include <time.h>
#include <ctime>

//new packages From R4
#include "json/header/json.h"
#include "udp/UDP.h"
//#include "time.h" //to meansure  time delay


#include <sys\stat.h>       // stat function to check file modification time
#include <cmath>
#include <Windows.h>
//opencv related


#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>

//--------bell lab
#include <cv.h>			// OpenCV header file
#include <cxcore.h>     // OpenCV header file
#include "cvaux.h"

#include <fgBgParams.h>
#include <fgBgFcts.h>
#include <ffmpeg/ffopencv.h>





using namespace cv;
using namespace std;
using namespace Json;    //json name space

/* Create the add-on message string table. */
#define JMESSAGE(code,string) string ,
static const char * const cdjpeg_message_table[] = { NULL };

// ****** PROGRAM-SPECIFIC SETTINGS *******
#define PRIVACYFLAG_DFLT 1      // 1 = fg privacy; 0 otherwise
#define CAMID_DFLT IPCAM_LOCAL  // camera default for this program  
#define IPCAM_DFLT "128.238.151.65"

#define DISPLAY_LEVEL_DFLT 3			// SAV scale that is displayed (can be changed during runtime)
#define TEXTURE_WNDW 17 //51		// for Difference of Texture segmentation
#define MIN_SIDE 3				// smallest sidelength of multi-scale blocks
/* fg->bg dissolve (or adapt) coefficient: small value dissolves quickly (0.5 is immediate); (0.999 is 33 sec)
 * for motion calculation, it is most convenient if ONLY motion is displayed, so coef. is chosen small
 * disadv. is that blue-man dissappears immediately for stationary people; but that is also adv. 
 * because if people stand too long, they blend into bg, then become blue man ghost when they move */
#define ALPHA_TCONST 0.5
#define DISPLAY_LEVEL_DFLT_POLY 4

#define BITSET_SIZE 12288	//128*96; /8=1536byte
/* ****** END PROGRAM-SPECIFIC SETTINGS ******* */

struct angleOrder angleOrder[3000];
struct IPcam
{
	char name[256];												// name of location of camera
	char ipAddress[MAX_IPCAMS];						// IP address of camera
	long *ptrPStream;											// pointer to pStream (not PanasonicStream so don't need those include files here)
	char login[256];											// login to ip cam
	char pwd[256];												// password to ipcam
};
#define AXIS_CGI "/axis-cgi/mjpg/video.cgi?resolution=640x480&compression=0&fps=20&.mjpg"  // portion of cgi command for ip cam open
#define IP_LOGIN_DFLT "root"
#define IP_PWD_DFLT "root123"

void usage (short flag);

//add by ray
string itoa(short value);
string writeIntArray(vector<short> vec);
string writeStrArray(vector<string> vec);


int input (int argc, char *argv[], char *vidFilenameIn, int *camID, struct IPcam *ipCam, short *privacyFlag, short *initBgImgFlag);
int runningInput (short IOflag, int key, short *setBGFlag, short *initBgImgFlag, short *privacyFlag, int iFrame, int *iFramePrivacyOn, long *displayLevel);
int getFrame (IplImage **current_frame, int camID, CvCapture* videoIn);
int videoParams (int camID, char *vidFilenameIn, struct IPcam *ipCam, CvCapture** videoIn,int *widVideo, int *htVideo, int *sizeVideo, int *fps);


//following functions in displayPoly.cpp 
void fgMaskPoly (IplImage *background_frame, IplImage *dotSSCurrent, IplImage *result_frame, int width, int height); 
void GetMotionInfo(IplImage *imgIn,struct Level *level,int ht, int wid, int curMotionDirt,int MotionLocX,int MotionLocY, int displayLevel);
void GetMulMotionInfo(IplImage *imgIn,struct Level *level,int ht, int wid, int curMotionDirt,vector<MotionRegion> * motionRegions);
void blockSAVPoly (IplImage *imgIn, IplImage *imgOutC, IplImage *background_frame, IplImage *result_frame, struct Level *level, long nLevels, int wid, int ht, int widOut, int htOut, long displayLevel,int iFrame);
void displayPoly (IplImage *result_frame, short *initDisplayFlag, int wid1, int ht1, int wid2, int ht2,vector<MotionRegion> * motionRegions);

int main(int argc, char** argv)
{
  char vidFilenameIn[256];              // video input filename; or if NULL, then camera input
  CvCapture* videoIn = 0;					        // video file in// video file in
	//CvCapture* camCvId;										// webcam camera (OpenCV identifier) -- couldn't replace VI with this - try with CV 2.0
  int device1 = DEVICE_NUM;				      // video device id number
  unsigned char *vidBuffer;				      // video buffer for frame capture
  float *bgEdgeArray;                   // bg edge array
  int widVideo, htVideo, sizeVideo;		  // video width, height, and total length (wid * ht)
  int sizeVideoC;												// color size
  int fps;								              // frames per second to control file video playback speed
  int nFramesTotal;						          // total number of video frames (for video file only)
  long widSS, htSS;                     // subsampled DoT image size
  short initBgImgFlag;                  // =1 to capture and store initial bg image; 0 otherwise
  short nextFrameFlag;					        // =1 if new frame available; 0 otherwise
  short initDisplayFlag = 0;            // initialize display = 0 if not initialized; 1 if initialized
  int key;								              // user keystroke input
  int iFrame;						                // index of video frame
  short privacyFlag;				            // 0=off, 1= private bg, 2= private fg, 3= private all (both)
  int iFramePrivacyOn = -1;							// timeout in frames for privacy flag to turn back on
  long nDiffPerFrame = 0;               // no. different texture elements per frame indicate activity
  
  
  int i;
  
/* background parameters */
  short setBgFlag = 2;			        // bg from file =1; manual reset =2; reset done this cycle =3; or =0
  int bgOnlyCounter = -1;				// counter assumes only bg input when flag > 0 [frames]; -1 to start stored image

/* IP camera parameters */
  int camID;                            // IP camera ID number
  struct IPcam ipCam;									// struct contains ip camera 
              // the stream class of IP camera
  char IPaddress[256], userName[256], passWord[256]; 
/* OpenCV structures for input and output images */
  IplImage *background_frame = 0;
  IplImage *diff_resultg = 0;
  IplImage *dotSSB4 = 0;            // subsampled DoT mask from previous frame
  IplImage *dotSSCurrent = 0;       // subsampled DoT mask from current frame
  IplImage *dotSSRegion = 0;        // subsampled DoT mask for display and debug
  IplImage *dirnSSMap = 0;						// direction map, 1-8 color on grayscale plane
  IplImage *dirnSSMapC = 0;						// direction map, color
  IplImage *current_frame = 0;
  IplImage *scratch_frame1g = 0;		// scratch frame for temporary work
  IplImage *scratch_frame2g = 0;		// scratch frame for temporary work
  IplImage *result_frame = 0;		// result frame for processed image
  IplImage *bgMask_frameg = 0;       // full-sized bg mask image

/* SAV */
  long localMsgTime = 0;                // time of last input message from local message file
  short exitFlag = 0;                   // 1 = exit; 0 otherwise
  long nLevels;
  struct Level *level = NULL;
  long displayLevel;                 // level to display of SAV
  long minSide;                       // minimum sidelength (defines number of levels)
  long size;

  int curMotionDirt=0;
  vector<MotionRegion> motionRegions; // store all the motion region info


//=============================================================================
//==================================init ======================================
//=============================================================================
/* command-line input */
  if (input (argc, argv, vidFilenameIn, &camID, &ipCam, &privacyFlag, &initBgImgFlag) < 0) 
    return(-1);

/* Video Input options: file, webcam, or IP cam */
/* file input */
  videoParams (camID, vidFilenameIn, &ipCam, &videoIn, &widVideo, &htVideo, &sizeVideo, &fps);

/* initialize Scene Activity Vector (SAV) */
  widSS = widVideo/BGMASK_SUBSAMPLE;
  htSS = htVideo/BGMASK_SUBSAMPLE;
  printf("Unit(bgmask_subsample): %d , widSS:%ld,htSS:%ld \n", BGMASK_SUBSAMPLE, widSS ,htSS);
  minSide = MIN_SIDE;
  
  initSAV (&level, &nLevels, minSide, widSS, htSS);
  displayLevel = DISPLAY_LEVEL_DFLT_POLY;

/* allocate memory for video frames */ 
  background_frame = cvCreateImage(cvSize(widVideo,htVideo),IPL_DEPTH_8U,3);
  diff_resultg = cvCreateImage(cvSize(widVideo,htVideo),IPL_DEPTH_8U,1);
  current_frame = cvCreateImage(cvSize(widVideo,htVideo),IPL_DEPTH_8U,3);
  scratch_frame1g = cvCreateImage(cvSize(widVideo,htVideo),IPL_DEPTH_8U,1);
  scratch_frame2g = cvCreateImage(cvSize(widVideo,htVideo),IPL_DEPTH_8U,1);
  result_frame = cvCreateImage(cvSize(widVideo,htVideo),IPL_DEPTH_8U,3);
  bgMask_frameg = cvCreateImage(cvSize(widVideo,htVideo),IPL_DEPTH_8U,1);

/* allocate and initialize SAV images */
  dotSSB4 = cvCreateImage(cvSize(widSS, htSS),IPL_DEPTH_8U,1);            // note "SS" = subsampled
  dotSSCurrent = cvCreateImage(cvSize(widSS, htSS),IPL_DEPTH_8U,1);
  dotSSRegion = cvCreateImage(cvSize(widSS, htSS),IPL_DEPTH_8U,1);
  dirnSSMap = cvCreateImage(cvSize(widSS, htSS),IPL_DEPTH_8U,1);
  dirnSSMapC = cvCreateImage(cvSize(widSS, htSS),IPL_DEPTH_8U,3);
  size = widSS * htSS;
  for (i = 0; i < size; i++)
    dotSSB4->imageData[i] = (uchar)0;

/* allocate and initialize edge array */
  bgEdgeArray = new float[sizeVideo];
  for (i = 0; i < sizeVideo; i++)
    bgEdgeArray[i] = 0.0;

/* initialize for frame capture loop and display running loop options to user */
  iFrame = 0;
 sizeVideoC = sizeVideo * 3;		// color size
  runningInput (0, 0, &setBgFlag, &initBgImgFlag, &privacyFlag, iFrame, &iFramePrivacyOn, &displayLevel);

/* angle span initialization code */
  angleSpan (angleOrder, TEXTURE_WNDW);


//UDP setup
	UDPConn udpClient= UDPConn();
	udpClient.open();
	
//fixbyRaybit:4.1 test time cost of each part
	clock_t Atime,Atime2,Atime3,Atime4,Atime5,Atime6,Atime7,Atime8,Btime,Ctime,Ctime2,Ctime3,Dtime,Etime;
	int timePass;
	int frameRate = 50;

//addbyRaybit

		vector<short> rowVec;
		vector<string> imgVec;

//=============================================================================
//==================================start ======================================
//=============================================================================
  while (1) {	

Atime=clock();
  /* if user keystroke, set flags, or break and exit */
		if (_kbhit()) {
			key = _getch();
			if (runningInput (1, key, &setBgFlag, &initBgImgFlag, &privacyFlag, iFrame, &iFramePrivacyOn, &displayLevel)) break;	
		}


nextFrameFlag = getFrame (&current_frame, camID, videoIn);
Atime2=clock();
		if (nextFrameFlag)
		{
			iFrame++;


	/* if command line option to initialize bg img to file, then do so and exit */
			//if (initBgImgFlag == 2) { cannedBgImg (current_frame, WEBCAM); break; }

		/* reset bg if flag set (=1 new camera, =2 manual reset) */
      if (setBgFlag == 2){
				initBg4Edge (current_frame, background_frame, &setBgFlag, camID, widVideo, htVideo);
	  }
		/* perform difference of edge images */
    	nDiffPerFrame = diffOfEdgeImg(current_frame, bgEdgeArray, scratch_frame1g, scratch_frame2g,
                        WIN_LEN, diff_resultg, ALPHA_TCONST, MASK_RSLT_FG, &setBgFlag, camID, widVideo, htVideo);
 Atime3=clock();
		/* segment by finding texture regions to obtain fgbg mask */
    /* TFLTR set for motion blur (vs. anti-flicker); MASK_RSLT_FG set to obtain fg */
      textureSeg (current_frame, diff_resultg, dotSSCurrent, dotSSRegion, bgMask_frameg, 
                      angleOrder, TEXTURE_WNDW, MASK_RSLT_FG, TFLTR_MOTIONBLUR, widVideo, htVideo);

Atime4=clock();
		/* SAV */
      motionSAV (dotSSCurrent, dotSSB4, dirnSSMap, level, nLevels, widSS, htSS, displayLevel);
Atime5=clock();
	  /*Get the direction from the motion block*/
	  //GetMotionInfo(dirnSSMap,level,curMotionDirt,widSS, htSS,MotionLocX,MotionLocY,displayLevel);

	  GetMulMotionInfo(dirnSSMap,level,htSS,widSS,curMotionDirt,&motionRegions);
Atime6=clock();

		//udp transfer json data

		//Value jsonValue,objList;
		vector<short> rectVec;
		vector<MotionRegion>::iterator it;
		
		//int mListLen =0;
		for(it=motionRegions.begin();it<motionRegions.end();it++)
		{  
			//mListLen++;
			Value item;
			//it->center.x*BGMASK_SUBSAMPLE,it->center.y*BGMASK_SUBSAMPLE,it->height*BGMASK_SUBSAMPLE,it->width*BGMASK_SUBSAMPLE,it->dirt,it->cellSize,idx);
			/*
			item.append( it->center.x*BGMASK_SUBSAMPLE).asInt();
			item.append( it->center.y*BGMASK_SUBSAMPLE).asInt();
			item.append( it->height*BGMASK_SUBSAMPLE).asInt();
			item.append( it->width*BGMASK_SUBSAMPLE).asInt();
			item.append( it->dirt).asInt();
			item.append( it->cellSize).asInt();
			*/
			rectVec.push_back(it->center.x*BGMASK_SUBSAMPLE);
			rectVec.push_back(it->center.y*BGMASK_SUBSAMPLE);
			rectVec.push_back(it->height*BGMASK_SUBSAMPLE);
			rectVec.push_back(it->width*BGMASK_SUBSAMPLE);
			rectVec.push_back(it->dirt*BGMASK_SUBSAMPLE);
			rectVec.push_back(it->cellSize);
		}

		string rectVecStr = writeIntArray(rectVec);
		//jsonValue.append(mListLen); // the length of obj
		//jsonValue.append(objList);
		//jsonValue["ml"]=objList;

Atime7=clock();

		//pack image region
		//Value imageMartix=Value(arrayValue);
		short yy,xx,idx,counter,tmp,rowIndex;
		//Value rowList;

		
		bool isPreBlack,isBlack;

	
	    for (yy = 0; yy < htSS; yy++){
			//rowList= Value(arrayValue);
			counter =0;
			
			for (xx = 0; xx < widSS; xx++){
				
				idx = yy * widSS + xx;
				isBlack = (bool)(uchar) dirnSSMap->imageData[idx];
				if(xx==0){
					//rowHead
					counter=1; 
					if(isBlack){
						isPreBlack=true;
						rowVec.push_back(1);
					}else{

						isPreBlack=false;
						rowVec.push_back(0);
					}				
				}else if(xx==widSS-1){
					//rowTail
					if(isBlack ==isPreBlack){
						counter++;
						tmp =(short)isPreBlack;
					

						//rowList.append(tmp).asInt(); //use 0,1  
						//rowList.append(counter).asInt();
	
						//rowVec.push_back(tmp);
						rowVec.push_back(counter);
					}else{
						tmp =(short)isPreBlack;
						//rowList.append(tmp).asInt(); 
						//rowList.append(counter).asInt();
					
						//rowVec.push_back(tmp);
						rowVec.push_back(counter);

						//tmp =(short)isBlack;
						//rowList.append(isBlack).asInt(); 
						//rowList.append(1).asInt();
					
						//rowVec.push_back(isBlack);
						rowVec.push_back(1);

					}
				}else{
					if(isBlack ==isPreBlack){
						//if same color, continue 
						counter++;
					}else{
						//if not same,do record and start new section
						//tmp =(short)isPreBlack;
						//rowList.append(tmp).asInt(); //use 0,1 for bool
						//rowList.append(counter).asInt();
	
						//rowVec.push_back(tmp);
						rowVec.push_back(counter);

						//reset
						isPreBlack =isBlack;
						counter=1;
					}
				}
				
			}// end row
			//imageMartix.append(rowList);
			
			imgVec.push_back( writeIntArray(rowVec) );
			rowVec.clear();
		}
		string imgVecStr = writeStrArray( imgVec);
		imgVec.clear();
		//jsonValue.append(imageMartix);
		//jsonValue["bg"]=imageMartix;
		//jsonValue["ft"]=0;//format num 0 == main pkg
		
		string jsonPkg = "{\"ft\":0,\"bg\":"+imgVecStr+",\"ml\":"+rectVecStr+"}\n";
			
		printf ("%s", jsonPkg);
//Atime8=clock();
		//FastWriter fw;

		//udpClient.sendData(fw.write(jsonValue).c_str());
		udpClient.sendData(jsonPkg.c_str());

Ctime=clock();

		/* privacy or not */
			if (privacyFlag)
				fgMaskPoly (background_frame, dotSSCurrent, result_frame, widVideo, htVideo);
			else
				for (i = 0; i < sizeVideo; i++)
					result_frame->imageData[i] = current_frame->imageData[i];

		/* color code per SAV blocks, and display */
        blockSAVPoly (dirnSSMap, dirnSSMapC, background_frame, result_frame, level, nLevels, 
                      widSS, htSS, widVideo, htVideo, displayLevel, iFrame);
		
		//Test pixels transfer
		//128*96

		//show line from config file
		/*
		for(int rIdx=0; rIdx<rangeNum;rIdx++){
			
			cvLine(result_frame,rangePoint[rIdx*2], rangePoint[rIdx*2+1], cv::Scalar(26,90,227), 5);
		}
		*/
			displayPoly (result_frame, &initDisplayFlag, widSS, htSS, widVideo, htVideo,&motionRegions);
			Dtime=clock();
			motionRegions.clear();
		/* write current DoT to B4 image for next iteration */
      	for (i = 0; i < size; i++)
        	dotSSB4->imageData[i] = dotSSCurrent->imageData[i];
	  }//if (nextFrameFlag)
		//else if (iFrame > 0) 
		//	printf ("No capture at frame number %d\n", iFrame);		// to indicate speed of frame request vs capability of network, etc.

	/* pause for a bit until next frame grab */
		if (camID == CAM_FILE){					// video from file
			cvWaitKey (1000 / fps);
			if (nextFrameFlag == 0) break;		// end of video file
		}
	
	//Etime=clock();
		

Ctime2=clock();	

		timePass = static_cast<int> (Ctime2-Atime)*1000/CLOCKS_PER_SEC;

		/* turn off unless do delay test*/
		if(nextFrameFlag  && timePass>60){
			/* printf("All:%d ms,1gF:%f,2dif:%f,3mSav:%f,4GMI:%f \n",timePass,
			double(Atime2 - Atime)/CLOCKS_PER_SEC,
			double(Atime3 - Atime2)/CLOCKS_PER_SEC,
			double(Atime5 - Atime4)/CLOCKS_PER_SEC);
			*/

			printf("All:%d ms,gap1:%f,gap2:%f,gap3:%f \n",timePass,
			double(Atime7 - Atime6)/CLOCKS_PER_SEC,
			//double(Atime8 - Atime7)/CLOCKS_PER_SEC);
			double(Ctime - Atime7)/CLOCKS_PER_SEC);
		}
		
		
		if(timePass>=frameRate-1){
	
			cvWaitKey(1);
		}else{

			cvWaitKey(frameRate-timePass); 
		}
	
	
	}
/* END OF FRAME CAPTURE LOOP ****************************************************/

/* close all cv processes, stop the input device, release memory, and end */
//   closeVideo (camID, vidFileIn, device1, vidBuffer, pStream);
   cvDestroyAllWindows();
 //mysql_close( sock)
   udpClient.close();
   
  return 0;
}

//only work for short int 0~9999
std::string itoa(short  value) {

                std::string buf;
				
                // enum { kMaxDigits = 35 };
                //buf.reserve( kMaxDigits ); // Pre-allocate enough space.
				buf.reserve(4);

                //short quotient = value;

                // Translating number to string with base:
                do {
                        buf += "0123456789"[ value % 10 ];
                        value /= 10;
                } while ( value );

                // Append the negative sign
                //if ( value < 0) buf += '-';

                std::reverse( buf.begin(), buf.end() );
                return buf;
        }

std::string writeIntArray(vector<short> verc)
{
		vector<short>::iterator begin_iter=verc.begin();
        vector<short>::iterator end_iter=verc.end();
		vector<short>::iterator iter;
		string doc="";
		short size=verc.size();
		doc += "[";
		for(short ix=0;ix<size;ix++)
		{
			if ( ix !=0 )
				doc += ",";

			doc += itoa(verc[ix] );

		}
		doc += "]";

		return doc;
}
std::string writeStrArray(vector<string> verc)
{
		vector<string>::iterator begin_iter=verc.begin();
        vector<string>::iterator end_iter=verc.end();
		vector<string>::iterator iter;
		string doc="";
		short size=verc.size();
		doc += "[";
		for(short ix=0;ix<size;ix++)
		{
			if ( ix !=0 )
				doc += ",";

			doc += verc[ix] ;
			
		}
		doc += "]";
		
		return doc;
}
 



/* VIDEOPARAMS -		function gets video parameters
 *			NOTE - this function has to stay in main file because VI is globally defined
 */
int videoParams (int camID, char *vidFilenameIn, struct IPcam *ipCam, CvCapture* *videoIn,int *widVideo, int *htVideo, int *sizeVideo, int *fps)
{
	printf ("1--> width = %d, height = %d, fps = %d\n", *widVideo, *htVideo, *fps);
/* get video input handle */
  char ipCam_link[256];
  if (camID == CAM_FILE){
	  printf ("001 file \n");
		*videoIn = cvCaptureFromFile(vidFilenameIn);		// capture from file
  }
  else if (camID == WEBCAM) {
	  printf ("002 webcam \n");
		*videoIn = cvCaptureFromCAM(0);							// capture from webcam
  }
  else{
		printf ("003 local ip \n");
		printf ("http://%s:%s@%s%s", ipCam->login, ipCam->pwd, ipCam->ipAddress, AXIS_CGI);

		sprintf(ipCam_link, "http://%s:%s@%s%s", ipCam->login, ipCam->pwd, ipCam->ipAddress, AXIS_CGI);
		*videoIn = cvCaptureFromFile(ipCam_link);
  }
  printf ("2-->  width = %d, height = %d, fps = %d\n", *widVideo, *htVideo, *fps);
/* if input fails to open, error condition */
	 if (videoIn == NULL) {
		 printf("ERROR: VIDEOPARAMS - cannot capture from video input\n");
		 return (-1);
	 }
	printf ("3--> width = %d, height = %d, fps = %d\n", *widVideo, *htVideo, *fps);

/* get capture parameter values */
	cvQueryFrame(*videoIn); // query to get capture properties 

	*htVideo = (int) cvGetCaptureProperty(*videoIn, CV_CAP_PROP_FRAME_HEIGHT);
	*widVideo = (int) cvGetCaptureProperty(*videoIn, CV_CAP_PROP_FRAME_WIDTH);
	*sizeVideo = *htVideo * *widVideo * 3;
	*fps = (int) cvGetCaptureProperty(*videoIn, CV_CAP_PROP_FPS);
	printf ("last Video Size: width = %d, height = %d, fps = %d\n", *widVideo, *htVideo, *fps);

	 return (0);
}



/* GETFRAME:    function grabs frame from whichever camera type and id is specified
 *              Note - the reason for **current_frame is that cvRetriveFrame retreives a pointer;
 *                     otherwise for webcam and ip cam input, only *current_frame is needed
 */
int getFrame (IplImage **current_frame, int camID, CvCapture* videoIn)
{

/* grab frame */
	*current_frame = cvQueryFrame(videoIn);

/* handle error condition for return*/ 
	if (*current_frame != NULL) {
	/* apparently file input has different origin than camera, so needs to be flipped */
		if (camID == CAM_FILE) cvFlip(*current_frame, NULL, 1);            
		return (1);
	}
	else return (0);
	//return (1);
}


/* CLOSEVIDEO - function closes video processes and releases memory


void closeVideo (int camID, CvCapture* vidFileIn, int device1, unsigned char *vidBuffer, PanasonicStream *pStream)
{

  if (camID == CAM_FILE)                  // close down for file
    cvReleaseCapture( &vidFileIn );
  else if (camID == WEBCAM){              // close down for webcam
    VI.stopDevice(device1);
    delete [] vidBuffer;
  }
  else if (camID > WEBCAM)                // close down for ip cameras
	pStream->~PanasonicStream();
}
 */

/* RUNNINGINPUT -	function displays menu choices to user and grabs user input while program running
 *				rtn = userIO (IO, ...)
 *							IO = 0 to display user message, 1 to grab user response
 *							rtn = 1 to exit; 0 otherwise
 */

int runningInput (short IOflag, int key, short *setBgFlag, short *initBgImgFlag, 
										short *privacyFlag, int iFrame, int *iFramePrivacyOn, long *displayLevel)
{

/* message to user on options */
  if (IOflag == 0){
    if (*initBgImgFlag == 0)
		  printf ("%s \n%s \n%s \n%s\n",
	      "Enter character for options:",
		    "\tr - Reset background (make sure foreground is clear, then reset.)",
        "\tp - Toggle on/off foreground privacy filter",
				"\tq - EXIT");
    else {
      printf ("Press b to store new background image file when no foreground activity\n");
      printf ("; or space to exit without storing.\n");
    }
  }

/* user input from menu options */
	else{
		if (key == 'r')	*setBgFlag = 2; // flag=2 manual reset (=1 for initial bg from file)
		else if (key == 'p') { // *privacyFlag = (*privacyFlag == 0) ? 1: 0;
			if (*privacyFlag == 0){
				*privacyFlag = 1;
				*iFramePrivacyOn = -1;
			}
			else{
				*privacyFlag = 0;
				*iFramePrivacyOn = iFrame + NFRAME_PRIVACY_TIMEOUT;
			}
		}
		else if (key == 'b'){
			*initBgImgFlag = 2;         // flag=2 causes bg img capture, storage and exit
			printf ("Initial background image is capture and stored. Goodbye.\n");
		}
		else if (key == '0' || key == '1' || key == '2' || key == '3' || key == '4' || key == '5'
              || key == '6' || key == '7' || key == '8' || key == '9'){
			*displayLevel = key - 48;
			printf ("Level = %d\n", *displayLevel);
		}
		else return (1);				// exit if any other key is pressed
	}

	return (0);
}


/* USAGE:       function gives instructions on usage of program
 *                    usage: usage: fgExtract param flags and values ...
 */

void usage (short flag)              /* flag =1 for long message; =0 for short */
{

/* print short usage message or long */
  if (flag != 0){
    printf ("USAGE: videocom \n");
    printf ("\tINPUTS:\n");
    printf ("\t\t-c <0 (webcam), 1 (IP cam dflt), or ip-addr of cam>\n");
    printf ("\t\t-b <0, 1, ip-addr> to initialize and store background image (then exit)\n");
    printf ("\t\t-iF <filename>\n");
    printf ("\t? or help - prints these parameter options");
  }
}


/* INPUT:       function reads input parameters
 */

#define USAGE_EXIT(VALUE) {usage (VALUE); return (-1);}

int input (int argc, char *argv[], char *vidFilenameIn, int *camID, struct IPcam *ipCam,
              short *privacyFlag, short *initBgImgFlag)
{
  long n;
	char camIDString[256];

/* general default values */
  *privacyFlag = PRIVACYFLAG_DFLT;
  *vidFilenameIn = NULL;
  *initBgImgFlag = 0;                 // initialize bg image if = 1; 0 otherwise
  *camID = CAMID_DFLT;

/* IP cam defaults */
	sprintf (ipCam->ipAddress, IPCAM_DFLT);
	sprintf (ipCam->name, "IP_Camera");
	sprintf (ipCam->login, IP_LOGIN_DFLT);
	sprintf (ipCam->pwd, IP_PWD_DFLT);

/* if "help" or "?" input, print command-line options */
	if (argc >= 2 && (!strcmp (argv[1], "help") || !strcmp (argv[1], "?"))) USAGE_EXIT (1);

/* read input parameter values */
  for (n = 1; n < argc; n++) {
    if (strcmp (argv[n], "-c") == 0){											// specify local camera mode
			if (++n >= argc) USAGE_EXIT (1);
			sprintf (camIDString, argv[n]);
			if (strcmp(camIDString, "0") == 0) 
				*camID = WEBCAM;																	// webcam
			else if (strcmp(camIDString, "1") == 0)							// ip cam of default address
				*camID = IPCAM_LOCAL;
			else{																								// ip cam of specified address
				*camID = 1;
				sprintf (ipCam->ipAddress, camIDString);
				if (argv[n + 1][0] != '-' && argc >= n + 2){			// login, pwd entered here as well for IP cam
					sprintf (ipCam->login, argv[++n]);
					sprintf (ipCam->pwd, argv[++n]);
				}

			}
    }
    else if (strcmp (argv[n], "-b") == 0){							// initialize and store bg image for camera
			if (++n >= argc) USAGE_EXIT (1);
			sprintf (camIDString, argv[n]);
			if (strcmp(camIDString, "0") == 0) 
				*camID = WEBCAM;																// webcam
			else if (strcmp(camIDString, "1") == 0)						// ip cam of default address
				*camID = IPCAM_LOCAL;
			else{																							// ip cam of specified address
				*camID = 1;
				sprintf (ipCam->ipAddress, camIDString);
				if (argv[n + 1][0] != '-' && argc >= n + 2){		// login, pwd entered here as well for IP cam
					sprintf (ipCam->login, argv[++n]);
					sprintf (ipCam->pwd, argv[++n]);
				}
			}
      *initBgImgFlag = 1;
    }
	/* file input */
    else if (strcmp (argv[n], "-iF") == 0){         
      strcpy (vidFilenameIn, argv[++n]);
      *camID = CAM_FILE;                            // video from file, not camera
    }
    else USAGE_EXIT (0);
  }
  return (0);
}