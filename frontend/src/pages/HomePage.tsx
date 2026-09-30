import React from 'react';
import { ArrowRight } from 'lucide-react';
import { useRoute } from '../app/AppRouter';
import { useLocalized } from '../app/localeContext';
import { homeContent } from '../content/home.content';
import { faqContent } from '../content/faq.content';
import { SectionContainer } from '../components/shared/SectionContainer';
import { Ribbon } from '../components/brand/Ribbon';
import { Medallion } from '../components/brand/Medallion';
import { FaqItem } from '../features/faq/components/FaqItem';

export const HomePage: React.FC = () => {
  const { navigate } = useRoute();
  const { hero, explanation, workflow, biomarkers, ctaBanner } = useLocalized(homeContent);
  const faq = useLocalized(faqContent);

  return (
    <div>
      {/* 1. Hero: the emblem draws itself while the name holds the page */}
      <section className="relative overflow-hidden -mt-[72px] pt-[72px]">
        {/* Desktop: the emblem bleeds off the top-right edge */}
        <Ribbon className="pointer-events-none absolute hidden lg:block -top-[34%] -right-[26%] w-[76%]" />

        <div className="relative max-w-[1240px] mx-auto px-5 sm:px-8 lg:px-12 min-h-[calc(100svh-72px)] flex flex-col">
          {/* Phones and tablets: the emblem owns its own band above the name */}
          <div className="lg:hidden relative h-[240px] sm:h-[320px] -mx-5 sm:-mx-8" aria-hidden="true">
            <Ribbon className="pointer-events-none absolute -top-[46%] -right-[18%] w-[118%] sm:w-[88%] sm:-right-[8%]" />
          </div>

          <div className="flex-1 flex flex-col justify-center pb-16 lg:pt-24 lg:pb-12 short:pt-4 short:pb-5">
          <div className="max-w-[760px]">
            <h1 className="rise-in text-[clamp(3.25rem,11vw,6rem)] short:text-[3.75rem] font-medium tracking-[-0.04em] leading-[0.95] text-ink">
              {hero.title}
            </h1>
            <p
              className="rise-in mt-4 short:mt-3 text-[clamp(2rem,5.6vw,3.75rem)] short:text-[2.375rem] font-medium tracking-[-0.035em] leading-[1.05] text-iris"
              style={{ animationDelay: '120ms' }}
            >
              {hero.tagline}
            </p>

            <div className="rise-in mt-10 max-w-[58ch] border-t border-line pt-8 short:mt-5 short:pt-4 short:max-w-[68ch]" style={{ animationDelay: '240ms' }}>
              <p className="text-lg sm:text-xl short:text-[17px] text-body leading-relaxed">{explanation.text}</p>
            </div>
          </div>
          </div>

          {/* The three seals, set along a hairline at the foot of the viewport */}
          <ul className="grid grid-cols-3 gap-4 sm:gap-6 border-t border-line py-6 sm:py-8 short:py-3">
            {biomarkers.items.map((item) => (
              <li key={item.id} className="flex flex-col sm:flex-row items-start sm:items-center gap-3 sm:gap-4">
                <Medallion
                  pattern={item.id}
                  className="w-16 sm:w-20 short:w-12 shrink-0 text-ink"
                />
                <span className="text-base sm:text-lg font-medium tracking-[-0.01em] text-ink">{item.name}</span>
              </li>
            ))}
          </ul>
        </div>
      </section>

      {/* 2. Workflow: three measured steps on one hairline */}
      <SectionContainer className="border-t border-line">
        <div className="grid grid-cols-12 gap-x-6 gap-y-12">
          <h2 className="col-span-12 lg:col-span-4 text-4xl sm:text-5xl font-medium tracking-[-0.03em] leading-[1.05] text-ink max-w-[14ch]">
            {workflow.heading}
          </h2>

          <ol className="col-span-12 lg:col-span-8 grid grid-cols-1 md:grid-cols-3 gap-x-8 gap-y-10">
            {workflow.steps.map((step, idx) => (
              <li key={step.number} className="relative pt-6 border-t border-ink/80">
                <span
                  className="absolute -top-[5px] left-0 w-2.5 h-2.5 rounded-full bg-iris ring-4 ring-ground"
                  aria-hidden="true"
                />
                <span className="tabular block text-5xl font-medium tracking-[-0.04em] text-iris" aria-hidden="true">
                  {step.number}
                </span>
                <h3 className="mt-6 text-2xl font-medium tracking-[-0.02em] text-ink">
                  <span className="sr-only">{step.number}. </span>
                  {step.title}
                </h3>
                <p className="mt-3 text-base text-body leading-relaxed">{step.description}</p>
                {idx < workflow.steps.length - 1 && (
                  <ArrowRight
                    className="hidden md:block absolute top-8 -right-6 w-4 h-4 text-line-strong"
                    aria-hidden="true"
                  />
                )}
              </li>
            ))}
          </ol>
        </div>
      </SectionContainer>

      {/* 3. Three patterns as engraved seals, set as a register */}
      <div className="bg-paper border-y border-line">
        <SectionContainer>
          <h2 className="text-4xl sm:text-5xl lg:text-6xl font-medium tracking-[-0.035em] leading-[1.02] text-ink">
            {biomarkers.heading}
          </h2>

          <ul className="mt-14 sm:mt-20 border-t border-line">
            {biomarkers.items.map((item) => (
              <li
                key={item.id}
                className="grid grid-cols-12 gap-x-6 gap-y-6 items-center py-10 sm:py-12 border-b border-line"
              >
                <div className="col-span-5 sm:col-span-3 lg:col-span-2">
                  <Medallion
                    pattern={item.id}
                    className="w-full max-w-[168px] text-ink"
                  />
                </div>
                <h3 className="col-span-7 sm:col-span-9 lg:col-span-3 lg:col-start-4 text-3xl sm:text-4xl font-medium tracking-[-0.03em] text-ink">
                  {item.name}
                </h3>
                <p className="col-span-12 lg:col-span-6 lg:col-start-7 text-lg text-body leading-relaxed max-w-[60ch]">
                  {item.description}
                </p>
              </li>
            ))}
          </ul>
        </SectionContainer>
      </div>

      {/* 4. FAQ: heading held left, register of questions right */}
      <SectionContainer>
        <div className="grid grid-cols-12 gap-x-6 gap-y-10">
          <div className="col-span-12 lg:col-span-4">
            <h2 className="lg:sticky lg:top-28 text-4xl sm:text-5xl font-medium tracking-[-0.03em] leading-[1.05] text-ink max-w-[14ch]">
              {faq.heading}
            </h2>
          </div>
          <div className="col-span-12 lg:col-span-8 border-t border-ink/80">
            {faq.items.map((item) => (
              <FaqItem key={item.id} item={item} />
            ))}
          </div>
        </div>
      </SectionContainer>

      {/* 5. Closing: the ink field */}
      <section className="relative overflow-hidden bg-ink-fill text-white">
        <Ribbon
          motion="none"
          showInk={false}
          density={22}
          className="pointer-events-none absolute opacity-45 -bottom-[40%] -right-[30%] w-[120%] sm:-right-[10%] sm:w-[70%] lg:bottom-auto lg:top-[-28%] lg:right-[-150px] lg:h-[150%] lg:w-auto lg:aspect-square"
        />
        <div className="relative max-w-[1240px] mx-auto px-5 sm:px-8 lg:px-12 py-20 sm:py-28">
          <div className="max-w-[640px]">
            <h2 className="text-4xl sm:text-5xl lg:text-6xl font-medium tracking-[-0.035em] leading-[1.02]">
              {ctaBanner.heading}
            </h2>
            <p className="mt-6 text-lg sm:text-xl text-[#d4d0f0] leading-relaxed max-w-[52ch]">
              {ctaBanner.description}
            </p>
            <button
              type="button"
              onClick={() => navigate('/screening')}
              className="group mt-10 inline-flex items-center gap-3 min-h-14 px-7 rounded-md bg-white text-ink-fill text-base font-medium hover:bg-lilac transition-colors cursor-pointer focus-visible:outline-white"
            >
              {ctaBanner.buttonText}
              <ArrowRight className="w-5 h-5 transition-transform group-hover:translate-x-0.5" aria-hidden="true" />
            </button>
          </div>
        </div>
      </section>
    </div>
  );
};
