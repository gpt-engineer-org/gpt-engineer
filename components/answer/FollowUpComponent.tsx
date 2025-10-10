import { IconPlus, IconClose } from '@/components/ui/icons';


// 1. Defines the FollowUp interface with a 'choices' property that contains an array of objects with a 'message' property, which in turn has a 'content' property of type string.
interface FollowUp {
    choices: {
        message: {
            content: string;
        };
    }[];
}

// 2. Defines the FollowUpComponent functional component that takes 'followUp' and 'handleFollowUpClick' as props.
const FollowUpComponent = ({ followUp, handleFollowUpClick }: { followUp: FollowUp; handleFollowUpClick: (question: string) => void }) => {
    const handleQuestionClick = (question: string) => {
        handleFollowUpClick(question);
    };

    return (
        <div className="dark:bg-slate-800 bg-white shadow-lg rounded-lg p-4 mt-4">
            <div className="flex items-center">
                <h2 className="text-lg font-semibold flex-grow dark:text-white text-black">Follow-Up</h2>
            </div>
            <ul className="mt-2">
                {followUp.choices[0].message.content && JSON.parse(followUp.choices[0].message.content).followUp.map((question: string, index: number) => (
                    <li
                        key={index}
                        className="flex items-center mt-2 cursor-pointer"
                        onClick={() => handleQuestionClick(question)}
                    >
                        <span role="img" aria-label="link" className="mr-2 dark:text-white text-black">
                            <IconPlus />
                        </span>
                        <p className="dark:text-white text-black hover:underline">{`${question}`}</p>
                    </li>
                ))}
            </ul>
        </div >
    );
};


export default FollowUpComponent;