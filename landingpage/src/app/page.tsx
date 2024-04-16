"use client";

import React from "react";

import Image from "next/image";
import {Typewriter} from 'react-simple-typewriter';

import MaintainanceImg from "../assets/maintenance.svg";
import WrenchScrewDriver from "@heroicons/react/24/solid/WrenchScrewdriverIcon";


export default function Home() {
  const handleType = (count: number) => {
    // access word count number
    console.log(count)
  }

  const handleDone = () => {
    console.log(`Done after 5 loops!`)
  }

  return (
    <div className="flex flex-col h-screen w-screen bg-white dark:bg-primary">
      <div className="flex flex-grow">
        <div className="flex flex-grow flex-col gap-1 justify-center items-center text-center lg:items-start lg:text-left lg:pl-16">

          <WrenchScrewDriver className="h-20 w-20 text-gray-300 mb-4" />

          <h3 className="text-6xl font-bold text-gray-900 dark:text-white">Coming Soon</h3>
          <p className="text-2xl text-gray-500 dark:text-gray-400 w-2/3 lg:w-full mt-2 lg:mt-2">
            <b>The World Calendar</b> is currently in the works.
            Follow us on <a href="https://twitter.com/thedonutlord239" className="text-blue-400 font-semibold">Twitter</a> or our blog for latest updates.
          </p>
          <p className="text-1xl text-gray-500 dark:text-gray-400 w-2/3 lg:w-full mt-2 lg:mt-2">
            <span>
              <Typewriter
                cursor
                words={["🛠️ Powered by Snazzy Studio"]}
                loop={1}
                typeSpeed={70}
                cursorStyle="_"
                deleteSpeed={50}
                delaySpeed={3000}
              />
            </span>
          </p>
        </div>

        <div className="lg:flex hidden flex-grow justify-center items-center">
          <Image alt="Image" width={900} height={900} src={MaintainanceImg} />
        </div>
      </div>
    </div>
  );
};
